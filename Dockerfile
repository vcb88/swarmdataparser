# Stage 1: Build the Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
# Debug: List context to see if files are available (this runs in the container, so it only sees what was copied)
# But we can't see the context *before* copying.
# Let's try to copy explicit file. If it fails here, it's missing from context.
COPY frontend/package.json ./
# Debug: Check if file exists after copy
RUN ls -la
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve with Backend
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy the build from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy other necessary files (import scripts, etc.)
COPY import_data.py verify_data.py ./

# Expose the port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
