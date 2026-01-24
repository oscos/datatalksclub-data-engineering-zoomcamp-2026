# Use a slim Python image
FROM python:3.13.1-slim-bookworm

# Copy uv binary (pinned version)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# 1. Copy dependency metadata first
# This layer is cached unless pyproject.toml or uv.lock changes
COPY pyproject.toml uv.lock ./

# 2. Install dependencies into the virtual environment
# --no-install-project skips installing the current project code at this stage
RUN uv sync --locked --no-install-project

# 3. Copy the rest of the application code
# Since this changes often, we put it near the end
COPY . .

# 4. Final sync to ensure the project itself is installed (if needed)
RUN uv sync --locked

# Always use the project venv
ENV PATH="/app/.venv/bin:$PATH"

# Default command: keep container alive
CMD ["bash"]