# Meridian Testing Guidelines

This document defines how developers should run tests, verify builds, and maintain testing standards in the Meridian project.

## 1. Backend Testing

### Step 1: Activate the Backend Virtual Environment

Run this command from the project root directory:

```powershell
.\src\backend\venv\Scripts\Activate.ps1
```

### Step 2: Install Backend Dependencies

```powershell
python -m pip install -r src/backend/requirements.txt
```

### Step 3: Run Backend Tests

```powershell
python -m pytest tests/backend -v
```

All backend tests should pass before submitting changes.

## 2. Frontend Build Verification

Navigate to the frontend directory:

```powershell
cd src/frontend
```

Install dependencies:

```powershell
npm ci
```

Build the frontend:

```powershell
npm run build
```

Return to the project root:

```powershell
cd ../..
```

The build must complete successfully without errors.

## 3. Test Directory Structure

Tests should be organized according to their purpose:

- `tests/backend/unit/`: Individual backend functions and components.
- `tests/backend/integration/`: Interactions between backend components and API endpoints.
- `tests/frontend/unit/`: Individual frontend components and functions.
- `tests/backend/conftest.py`: Shared pytest fixtures and test configuration.

## 4. Test Naming Convention

Use descriptive test names following this format:

`test_<what>_<expected>`

Examples:

- `test_application_health_returns_success`
- `test_unauthorized_user_cannot_access_protected_endpoint`
- `test_invalid_input_returns_validation_error`

Test names should clearly communicate the expected behaviour.

## 5. Test Case Requirements

Every newly implemented feature should include relevant test cases covering:

1. **Positive cases:** Verify that the feature works with valid inputs.
2. **Negative cases:** Verify that invalid inputs or unauthorized actions are handled correctly.
3. **Edge cases:** Verify boundary conditions and unusual scenarios.

Tests should verify actual application behaviour rather than simply checking that code executes.

## 6. Pull Request Requirements

Before submitting a pull request, developers must:

1. Run the relevant backend tests locally.
2. Verify that the frontend builds successfully.
3. Add appropriate tests for newly implemented functionality.
4. Ensure Feature CI completes successfully.
5. Review their changes before creating a pull request.
6. Resolve CI failures before requesting a merge.

Pull requests targeting `main` are additionally checked by the Meridian Pull Request CI workflow.

## 7. Test Environment and Security

- Automated tests must use the dedicated test database.
- Production database credentials must never be used for testing.
- Test data must remain separate from development and production data.
- Never commit `.env` files, passwords, API keys, or other sensitive credentials.
- CI workflows use temporary test credentials and isolated environments.
- Tests must not depend on sensitive information stored on a developer's local machine.

## 8. Continuous Integration

Meridian uses GitHub Actions for automated validation.

### Feature CI

Triggered whenever code is pushed to a branch matching `feature/**`.

It performs:

- Backend test execution.
- Frontend dependency installation.
- Frontend production build verification.

### Pull Request CI

Triggered whenever a pull request targets the `main` branch.

It performs:

- Backend test execution and test report generation.
- Frontend production build verification.
- Docker Compose configuration validation.
- Docker image building and service startup.
- Database migration execution.
- Backend and frontend health checks.
- Nginx backend proxy verification.

All required CI checks must pass before a pull request can be merged.