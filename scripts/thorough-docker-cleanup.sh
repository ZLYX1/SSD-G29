#!/bin/bash
# Script to thoroughly clean Docker resources and system disk space
# Use this script when encountering "no space left on device" errors

echo "🧹 Starting thorough Docker cleanup process..."

# Show disk usage before cleanup
echo "📊 Current disk space:"
df -h

# List largest directories
echo "📊 Largest directories in /var:"
du -h -d 2 /var | sort -hr | head -10

# Stop all running containers to ensure clean removal
echo "🛑 Stopping all containers..."
docker stop $(docker ps -aq) 2>/dev/null || echo "No containers to stop"

# Remove all containers
echo "🗑️ Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null || echo "No containers to remove"

# Remove all volumes (CAUTION: This will delete ALL data in volumes)
echo "🗑️ Removing all volumes..."
docker volume rm $(docker volume ls -q) 2>/dev/null || echo "No volumes to remove"

# Remove all images (CAUTION: This will delete ALL images)
echo "🗑️ Removing all images..."
docker rmi $(docker images -q) -f 2>/dev/null || echo "No images to remove"

# Clean up system packages
echo "🧹 Cleaning up system packages..."
apt-get clean -y
apt-get autoclean -y
apt-get autoremove -y

# Clean up Docker system
echo "🧹 Cleaning up Docker system..."
docker system prune -af --volumes

# Clean up log files that might be taking space
echo "🧹 Cleaning up log files..."
find /var/log -type f -name "*.log" -exec truncate -s 0 {} \;
find /var/log -type f -name "*.gz" -delete

# Show disk usage after cleanup
echo "📊 Current disk space after cleanup:"
df -h

echo "✅ Thorough Docker cleanup completed!"
