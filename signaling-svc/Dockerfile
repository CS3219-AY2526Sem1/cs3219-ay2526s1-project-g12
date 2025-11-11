# ---- Dockerfile ----
FROM node:18-alpine

COPY . /app

WORKDIR /app

# Install the application dependencies.
RUN npm install

# Expose signaling port
EXPOSE 4444

# Start the signaling server
CMD ["node", "./node_modules/y-webrtc/bin/server.js"]
