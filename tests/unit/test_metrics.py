# tests/unit/test_metrics.py
import pytest
from evaluation.metrics import compute_average_scores, find_best_prompt

def test_compute_average_scores_valid_results():
    results = [
        {"prompt": "casual", "route_feasibility": 0.9, "constraint_satisfaction": 0.85, "response_quality": 0.8, "total": 0.85, "comments": "Good"},
        {"prompt": "precise", "route_feasibility": 1.0, "constraint_satisfaction": 1.0, "response_quality": 1.0, "total": 1.0, "comments": "Excellent"},
        {"prompt": "scenic", "route_feasibility": 0.9, "constraint_satisfaction": 0.95, "response_quality": 0.9, "total": 0.9167, "comments": "Great"}
    ]
    avg_scores = compute_average_scores(results)
    assert avg_scores["prompts"] == ["casual", "precise", "scenic"]
    assert avg_scores["avg_route_feasibility"] == pytest.approx(0.9333, 0.001)
    assert avg_scores["avg_constraint_satisfaction"] == pytest.approx(0.9333, 0.001)
    assert avg_scores["avg_response_quality"] == pytest.approx(0.9, 0.001)
    assert avg_scores["avg_total"] == pytest.approx(0.9222, 0.001)

def test_compute_average_scores_empty_results():
    results = []
    avg_scores = compute_average_scores(results)
    assert avg_scores["prompts"] == []
    assert avg_scores["avg_route_feasibility"] == 0.0
    assert avg_scores["avg_constraint_satisfaction"] == 0.0
    assert avg_scores["avg_response_quality"] == 0.0
    assert avg_scores["avg_total"] == 0.0

def test_compute_average_scores_all_errors():
    results = [
        {"prompt": "casual", "error": "Failed"},
        {"prompt": "precise", "error": "Invalid"},
        {"prompt": "scenic", "error": "Error"}
    ]
    avg_scores = compute_average_scores(results)
    assert avg_scores["prompts"] == ["casual", "precise", "scenic"]
    assert avg_scores["avg_route_feasibility"] == 0.0
    assert avg_scores["avg_constraint_satisfaction"] == 0.0
    assert avg_scores["avg_response_quality"] == 0.0
    assert avg_scores["avg_total"] == 0.0

def test_find_best_prompt_valid_results():
    results = [
        {"prompt": "casual", "route_feasibility": 0.9, "constraint_satisfaction": 0.85, "response_quality": 0.8, "total": 0.85, "comments": "Good"},
        {"prompt": "precise", "route_feasibility": 1.0, "constraint_satisfaction": 1.0, "response_quality": 1.0, "total": 1.0, "comments": "Excellent"},
        {"prompt": "scenic", "route_feasibility": 0.9, "constraint_satisfaction": 0.95, "response_quality": 0.9, "total": 0.9167, "comments": "Great"}
    ]
    best_prompt = find_best_prompt(results)
    assert best_prompt["best_prompt"] == "precise"
    assert best_prompt["total_score"] == 1.0
    assert best_prompt["details"] == {
        "route_feasibility": 1.0,
        "constraint_satisfaction": 1.0,
        "response_quality": 1.0,
        "comments": "Excellent"
    }

def test_find_best_prompt_empty_results():
    results = []
    best_prompt = find_best_prompt(results)
    assert best_prompt["best_prompt"] is None
    assert best_prompt["total_score"] == 0.0
    assert best_prompt["details"] == {}

def test_find_best_prompt_all_errors():
    results = [
        {"prompt": "casual", "error": "Failed"},
        {"prompt": "precise", "error": "Invalid"},
        {"prompt": "scenic", "error": "Error"}
    ]
    best_prompt = find_best_prompt(results)
    assert best_prompt["best_prompt"] is None
    assert best_prompt["total_score"] == 0.0
    assert best_prompt["details"] == {}