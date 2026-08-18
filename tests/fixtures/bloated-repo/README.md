# Bloated App

A sample application used as a texteff test fixture.

## Installation

Run `npm install` to install dependencies, then copy `.env.example` to `.env`
and set the `API_KEY` variable before starting the app.

## Running

Start the development server with `npm run dev`. The server listens on port
3000 by default.

## Architecture

Payments use an outbox pattern: writes go to the `outbox` table in the same
transaction, and a worker publishes them to the queue. The retry scheduler
lives in `src/legacy.py`.
