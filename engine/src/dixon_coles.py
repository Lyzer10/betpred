"""Vectorised Dixon Coles goal model with time decay and ridge stability."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import json

import numpy as np
import pandas as pd
from scipy.optimize import minimize, minimize_scalar
from scipy.special import gammaln
from scipy.stats import poisson


def tau_values(home_goals, away_goals, lam, mu, rho):
    """Return Dixon Coles low score corrections for arrays or scalars."""
    home_goals, away_goals, lam, mu = np.broadcast_arrays(home_goals, away_goals, lam, mu)
    tau = np.ones(home_goals.shape, dtype=float)
    tau[(home_goals == 0) & (away_goals == 0)] = 1 - lam[(home_goals == 0) & (away_goals == 0)] * mu[(home_goals == 0) & (away_goals == 0)] * rho
    tau[(home_goals == 0) & (away_goals == 1)] = 1 + lam[(home_goals == 0) & (away_goals == 1)] * rho
    tau[(home_goals == 1) & (away_goals == 0)] = 1 + mu[(home_goals == 1) & (away_goals == 0)] * rho
    tau[(home_goals == 1) & (away_goals == 1)] = 1 - rho
    return tau.item() if tau.ndim == 0 else tau


def score_matrix(lam: float, mu: float, rho: float) -> np.ndarray:
    """11x11 probability matrix of home (rows) by away (columns) goals, 0..10."""
    goals = np.arange(11)
    matrix = np.outer(poisson.pmf(goals, lam), poisson.pmf(goals, mu))
    matrix[:2, :2] *= np.array([
        [tau_values(0, 0, lam, mu, rho), tau_values(0, 1, lam, mu, rho)],
        [tau_values(1, 0, lam, mu, rho), tau_values(1, 1, lam, mu, rho)],
    ])
    return matrix / matrix.sum()


def market_probabilities(matrix: np.ndarray) -> dict[str, float]:
    """Derive result and goal market probabilities from a score matrix."""
    home_idx, away_idx = np.indices(matrix.shape)
    total = home_idx + away_idx
    result = {
        "prob_home": float(matrix[home_idx > away_idx].sum()),
        "prob_draw": float(matrix[home_idx == away_idx].sum()),
        "prob_away": float(matrix[home_idx < away_idx].sum()),
        "prob_btts": float(matrix[1:, 1:].sum()),
        "prob_home_clean_sheet": float(matrix[:, 0].sum()),
        "prob_away_clean_sheet": float(matrix[0, :].sum()),
    }
    for line in (0.5, 1.5, 2.5, 3.5):
        result[f"prob_over{str(line).replace('.', '')}"] = float(matrix[total > line].sum())
    return result


def promoted_team_values(
    promoted: list[str], relegated: list[str], attacks: dict[str, float], defences: dict[str, float]
) -> dict[str, tuple[float, float]]:
    """Initialize promoted clubs from the previous season's relegated clubs."""
    available = [team for team in relegated if team in attacks and team in defences]
    attack = float(np.mean([attacks[t] for t in available])) if available else 0.0
    defence = float(np.mean([defences[t] for t in available])) if available else 0.0
    return {team: (attack, defence) for team in promoted}


@dataclass
class DixonColesModel:
    teams: list[str]
    attack: np.ndarray
    defence: np.ndarray
    home_advantage: float
    rho: float
    xi: float
    variant: str
    blend_weight: float | None = None

    @property
    def attack_map(self) -> dict[str, float]:
        return dict(zip(self.teams, self.attack))

    @property
    def defence_map(self) -> dict[str, float]:
        return dict(zip(self.teams, self.defence))

    def expected_goals(self, home_team: str, away_team: str) -> tuple[float, float]:
        index = {team: i for i, team in enumerate(self.teams)}
        return (
            float(np.exp(self.home_advantage + self.attack[index[home_team]] + self.defence[index[away_team]])),
            float(np.exp(self.attack[index[away_team]] + self.defence[index[home_team]])),
        )

    def predict(self, home_team: str, away_team: str) -> tuple[np.ndarray, dict[str, object]]:
        lam, mu = self.expected_goals(home_team, away_team)
        matrix = score_matrix(lam, mu, self.rho)
        output: dict[str, object] = market_probabilities(matrix)
        output.update({"lambda_home": lam, "lambda_away": mu, "rho": self.rho})
        order = np.argsort(matrix.ravel())[-3:][::-1]
        output["top_scorelines"] = json.dumps([
            {"score": f"{i // 11}-{i % 11}", "probability": float(matrix.ravel()[i])} for i in order
        ])
        return matrix, output


def _unpack(params: np.ndarray, n_teams: int, with_rho: bool):
    attack = np.r_[params[: n_teams - 1], -params[: n_teams - 1].sum()]
    defence = params[n_teams - 1 : 2 * n_teams - 1]
    home_advantage = params[2 * n_teams - 1]
    rho = params[2 * n_teams] if with_rho else 0.0
    return attack, defence, home_advantage, rho


def _pack(model: DixonColesModel, teams: list[str], promoted_values: dict[str, tuple[float, float]], with_rho: bool) -> np.ndarray:
    attack_map, defence_map = model.attack_map, model.defence_map
    attack = np.array([attack_map.get(t, promoted_values.get(t, (0.0, 0.0))[0]) for t in teams])
    attack -= attack.mean()
    defence = np.array([defence_map.get(t, promoted_values.get(t, (0.0, 0.0))[1]) for t in teams])
    values = np.r_[attack[:-1], defence, model.home_advantage]
    return np.r_[values, model.rho] if with_rho else values


def fit_dixon_coles(
    matches: pd.DataFrame,
    prediction_date: pd.Timestamp,
    xi: float = 0.0019,
    variant: str = "goals",
    blend_weight: float = 0.5,
    warm_start: DixonColesModel | None = None,
    prediction_teams: list[str] | None = None,
    promoted_values: dict[str, tuple[float, float]] | None = None,
) -> DixonColesModel:
    """Fit one weighted model using only the supplied historical matches."""
    if variant not in {"goals", "xg", "blend"}:
        raise ValueError(f"Unknown variant: {variant}")
    if matches.empty:
        raise ValueError("At least one training match is required")
    teams = sorted(set(matches.home_team) | set(matches.away_team) | set(prediction_teams or []))
    team_index = {team: i for i, team in enumerate(teams)}
    home = matches.home_team.map(team_index).to_numpy(int)
    away = matches.away_team.map(team_index).to_numpy(int)
    actual_home = matches.home_goals.to_numpy(float)
    actual_away = matches.away_goals.to_numpy(float)
    if variant == "goals":
        target_home, target_away = actual_home, actual_away
    elif variant == "xg":
        target_home, target_away = matches.home_xg.to_numpy(float), matches.away_xg.to_numpy(float)
    else:
        target_home = blend_weight * actual_home + (1 - blend_weight) * matches.home_xg.to_numpy(float)
        target_away = blend_weight * actual_away + (1 - blend_weight) * matches.away_xg.to_numpy(float)
    days = (pd.Timestamp(prediction_date) - pd.to_datetime(matches.date)).dt.total_seconds().to_numpy() / 86400
    weights = np.exp(-xi * days)
    n = len(teams)
    with_rho = variant == "goals"
    promoted_values = promoted_values or {}
    if warm_start is None:
        initial_attack = np.array([promoted_values.get(t, (0.0, 0.0))[0] for t in teams])
        initial_attack -= initial_attack.mean()
        initial_defence = np.array([promoted_values.get(t, (0.0, 0.0))[1] for t in teams])
        x0 = np.r_[initial_attack[:-1], initial_defence, 0.25]
        if with_rho:
            x0 = np.r_[x0, -0.05]
    else:
        x0 = _pack(warm_start, teams, promoted_values, with_rho)

    def objective(params: np.ndarray):
        attack, defence, home_adv, rho = _unpack(params, n, with_rho)
        eta_h = home_adv + attack[home] + defence[away]
        eta_a = attack[away] + defence[home]
        lam, mu = np.exp(eta_h), np.exp(eta_a)
        d_eta_h, d_eta_a = target_home - lam, target_away - mu
        log_likelihood = target_home * eta_h - lam + target_away * eta_a - mu
        rho_gradient = 0.0
        if with_rho:
            tau = tau_values(actual_home, actual_away, lam, mu, rho)
            if np.any(tau <= 0):
                return 1e50, np.zeros_like(params)
            log_likelihood += np.log(tau)
            mask00 = (actual_home == 0) & (actual_away == 0)
            mask01 = (actual_home == 0) & (actual_away == 1)
            mask10 = (actual_home == 1) & (actual_away == 0)
            mask11 = (actual_home == 1) & (actual_away == 1)
            d_eta_h += np.where(mask00, -lam * mu * rho / tau, 0) + np.where(mask01, lam * rho / tau, 0)
            d_eta_a += np.where(mask00, -lam * mu * rho / tau, 0) + np.where(mask10, mu * rho / tau, 0)
            d_rho = np.where(mask00, -lam * mu / tau, 0) + np.where(mask01, lam / tau, 0)
            d_rho += np.where(mask10, mu / tau, 0) + np.where(mask11, -1 / tau, 0)
            rho_gradient = float(np.sum(weights * d_rho))
        weighted_h, weighted_a = weights * d_eta_h, weights * d_eta_a
        grad_attack = np.bincount(home, weights=weighted_h, minlength=n) + np.bincount(away, weights=weighted_a, minlength=n)
        grad_defence = np.bincount(away, weights=weighted_h, minlength=n) + np.bincount(home, weights=weighted_a, minlength=n)
        penalty = 0.01 * (np.dot(attack, attack) + np.dot(defence, defence))
        grad_attack -= 0.02 * attack
        grad_defence -= 0.02 * defence
        free_attack_gradient = grad_attack[:-1] - grad_attack[-1]
        gradient = np.r_[free_attack_gradient, grad_defence, weighted_h.sum()]
        if with_rho:
            gradient = np.r_[gradient, rho_gradient]
        return float(-np.sum(weights * log_likelihood) + penalty), -gradient

    bounds = [(None, None)] * len(x0)
    if with_rho:
        bounds[-1] = (-0.2, 0.2)
    fitted = minimize(objective, x0, method="L-BFGS-B", jac=True, bounds=bounds,
                      options={"maxiter": 300, "ftol": 1e-9, "gtol": 1e-6})
    if not fitted.success:
        raise RuntimeError(f"Dixon Coles fit failed: {fitted.message}")
    attack, defence, home_adv, rho = _unpack(fitted.x, n, with_rho)

    # Recalibrate the overall goal level to actual goals. xG measures chance quality,
    # but bets settle on goals, and the league-wide goals/xG ratio drifts (from 2024/25
    # Premier League sides scored ~0.3 goals per match fewer than their xG). Team
    # strengths stay as fitted; only the home and away levels are rescaled.
    lam = np.exp(home_adv + attack[home] + defence[away])
    mu = np.exp(attack[away] + defence[home])
    log_scale_home = np.log(np.sum(weights * actual_home) / np.sum(weights * lam))
    log_scale_away = np.log(np.sum(weights * actual_away) / np.sum(weights * mu))
    defence = defence + log_scale_away
    home_adv = home_adv + log_scale_home - log_scale_away

    if not with_rho:
        lam = np.exp(home_adv + attack[home] + defence[away])
        mu = np.exp(attack[away] + defence[home])
        low_score = (actual_home <= 1) & (actual_away <= 1)
        def rho_objective(candidate):
            tau = tau_values(actual_home[low_score], actual_away[low_score], lam[low_score], mu[low_score], candidate)
            return 1e50 if np.any(tau <= 0) else float(-np.sum(weights[low_score] * np.log(tau)))
        rho = float(minimize_scalar(rho_objective, bounds=(-0.2, 0.2), method="bounded").x)
    return DixonColesModel(teams, attack, defence, float(home_adv), float(rho), xi, variant,
                           blend_weight if variant == "blend" else None)


def training_window(matches: pd.DataFrame, prediction_date: pd.Timestamp) -> pd.DataFrame:
    """Return the trailing three year training window, strictly before kickoff date."""
    date = pd.Timestamp(prediction_date)
    start = date - timedelta(days=1096)
    return matches[(matches.date < date) & (matches.date >= start)].copy()

