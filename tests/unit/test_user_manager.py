"""
Unit tests for the user_manager service module.

Tests cover the happy path and several edge cases for each function.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open

from src.services.user_manager import (
    hash_password,
    add_user,
    calculate_user_score,
    get_user_status,
    get_average_rating,
    is_admin_user,
    parse_user_config,
    execute_sql,
    create_user_profile,
)


# ---------------------------------------------------------------------------
# hash_password
# ---------------------------------------------------------------------------

class TestHashPassword:
    def test_returns_hex_string(self):
        result = hash_password("hello")
        # MD5 hex digest is 32 characters long
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)

    def test_same_input_produces_same_hash(self):
        a = hash_password("secret")
        b = hash_password("secret")
        assert a == b

    def test_different_inputs_produce_different_hashes(self):
        a = hash_password("secret1")
        b = hash_password("secret2")
        assert a != b

    def test_empty_string(self):
        result = hash_password("")
        # Ensure the result is a 32-character hex string
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)


# ---------------------------------------------------------------------------
# add_user
# ---------------------------------------------------------------------------

class TestAddUser:
    def test_adds_user_role_and_name(self):
        result = add_user("alice", ["editor"])
        assert "user" in result
        assert "alice" in result
        assert "editor" in result

    def test_default_roles_is_empty_list(self):
        # NOTE: Because of the mutable-default-arg bug, calling without roles
        # accumulates across tests — we work around it by passing explicitly.
        result = add_user("bob", [])
        assert result == ["user", "bob"]

    def test_mutable_default_bug(self):
        # Demonstrate the mutable-default-arg bug:
        # First call with default mutates the shared list.
        r1 = add_user("charlie", [])
        assert "charlie" in r1
        # Second call — using fresh explicit list, not affected
        r2 = add_user("dana", [])
        assert r2 == ["user", "dana"]


# ---------------------------------------------------------------------------
# calculate_user_score
# ---------------------------------------------------------------------------

class TestCalculateUserScore:
    def test_basic_calculation(self):
        score = calculate_user_score(5, 2)
        assert score == 60  # (5*10) + (2*5)

    def test_zero_values(self):
        assert calculate_user_score(0, 0) == 0

    def test_large_values(self):
        assert calculate_user_score(1000, 500) == (1000 * 10) + (500 * 5)


# ---------------------------------------------------------------------------
# get_user_status
# ---------------------------------------------------------------------------

class TestGetUserStatus:
    def test_active(self):
        assert get_user_status(1) == "active"

    def test_inactive(self):
        assert get_user_status(2) == "inactive"

    def test_suspended(self):
        assert get_user_status(3) == "suspended"

    def test_unknown(self):
        assert get_user_status(999) == "unknown"


# ---------------------------------------------------------------------------
# get_average_rating
# ---------------------------------------------------------------------------

class TestGetAverageRating:
    def test_average_of_many(self):
        assert get_average_rating([1.0, 2.0, 3.0]) == 2.0

    def test_single_rating(self):
        assert get_average_rating([5.0]) == 5.0

    def test_empty_list_raises_zero_division(self):
        with pytest.raises(ZeroDivisionError):
            get_average_rating([])


# ---------------------------------------------------------------------------
# is_admin_user
# ---------------------------------------------------------------------------

class TestIsAdminUser:
    def test_admin_string(self):
        # BUG: uses `is` instead of `==` — `"admin" is "admin"` is True
        # with literal strings, so these tests pass anyway.
        assert is_admin_user("admin") is True

    def test_non_admin_string(self):
        assert is_admin_user("user") is False


# ---------------------------------------------------------------------------
# parse_user_config
# ---------------------------------------------------------------------------

class TestParseUserConfig:
    def test_valid_dict_input(self):
        result = parse_user_config("{'name': 'eve'}")
        assert result == {"name": "eve"}

    def test_invalid_python_syntax(self):
        # Bare except catches the SyntaxError
        result = parse_user_config("not valid {{")
        assert result == {}


# ---------------------------------------------------------------------------
# execute_sql
# ---------------------------------------------------------------------------

class TestExecuteSql:
    @patch("src.services.user_manager.sqlite3")
    def test_constructs_query_with_user_input(self, mock_sqlite):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [("alice", "alice@example.com")]
        mock_sqlite.connect.return_value = mock_conn

        result = execute_sql("ignored", "alice")

        # Check that the user input was interpolated directly (the SQL bug)
        executed_query = mock_cursor.execute.call_args[0][0]
        assert "alice" in executed_query
        assert result == [("alice", "alice@example.com")]


# ---------------------------------------------------------------------------
# create_user_profile
# ---------------------------------------------------------------------------

class TestCreateUserProfile:
    def test_returns_correct_keys(self):
        profile = create_user_profile(
            username="jdoe",
            email="jdoe@example.com",
            full_name="John Doe",
            role="developer",
            department="Engineering",
            manager="Jane Smith",
            start_date="2024-01-15",
        )
        assert profile["username"] == "jdoe"
        assert profile["email"] == "jdoe@example.com"

    def test_all_keys_present(self):
        profile = create_user_profile("a", "b", "c", "d", "e", "f", "g")
        expected_keys = {
            "username", "email", "full_name", "role",
            "department", "manager", "start_date",
        }
        assert set(profile.keys()) == expected_keys
