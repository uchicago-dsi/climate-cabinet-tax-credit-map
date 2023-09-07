# Select base image
FROM node:alpine

# Set working directory
WORKDIR /app

# Copy node packages
COPY package*.json /app

# Install dependencies
RUN npm install

# Copy the remaining app components
COPY . /app

# Expose port for app development server
EXPOSE 3000

# Run the Next.js app upon container start
CMD ["npm", "run", "dev"]