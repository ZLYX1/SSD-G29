#!/bin/bash
# Script to clean up Docker resources to free disk space
# Useful for CI/CD environments or servers with limited disk space

echo "🧹 Starting Docker cleanup process..."

# Remove all stopped containers
echo "🗑️ Removing stopped containers..."
docker container prune -f

# Remove unused images
echo "🗑️ Removing dangling images..."
docker image prune -f

# Remove unused volumes (be careful with this one)
echo "🗑️ Removing unused volumes..."
docker volume prune -f

# Remove unused networks
echo "🗑️ Removing unused networks..."
docker network prune -f

# For more aggressive cleanup, uncomment the following line
# This will remove all images that aren't being used by a container
# docker image prune -a -f

# Show disk usage after cleanup
echo "📊 Current Docker disk usage:"
docker system df

echo "✅ Docker cleanup completed!"
