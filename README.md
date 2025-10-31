# KORA

A travel planner that calculates carbon footprints to help you make better decisions about your travel routes and methods.

[![Next.js](https://img.shields.io/badge/Next.js-15.5-black)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.1-blue)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-green)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-orange)](https://www.langchain.com/)

## Inspiration

There's a lot of information out there about climate change and carbon footprints, but it can be overwhelming. We built KORA to simplify those decisions that we don't always have time to think through with everything else going on.

## What it does

KORA is a travel planner with an AI assistant that helps you plan trips while keeping track of your carbon footprint. You can pick your destination country, choose cities to visit, and get recommendations for landmarks. The AI gives you insights into how your trip impacts the planet as you plan.

## Tech Stack

### Frontend
- Next.js 15.5 with React 19.1
- TypeScript
- TailwindCSS 4
- Globe.gl and Framer Motion for 3D visualizations
- React Markdown for rendering AI responses

### Backend
- Flask 2.3
- Python
- LangChain for orchestrating AI agents
- Google Gemini API for the conversational AI
- SQLite with SQLAlchemy
- Auth0 for authentication
- Various APIs:
  - GeoDB Cities (via RapidAPI) for location data
  - OpenTripMap for points of interest
  - OpenRouteService for distance calculations
  - Amadeus API for flight and hotel data

## Getting Started

### Prerequisites

You'll need:
- Node.js 18+ and npm
- Python 3.8+
- An Auth0 account
- A Google Gemini API key
- A RapidAPI key (for GeoDB Cities)
- An OpenTripMap API key
- An OpenRouteService API key
- Amadeus API credentials (optional, but useful for flight/hotel data)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd KORA
   ```

2. Set up the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

   Copy the example env file and fill in your keys:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your actual API keys:
   ```env
   GOOGLE_API_KEY=your-google-api-key
   RAPIDAPI_KEY=your-rapidapi-key
   AUTH0_DOMAIN=your-auth0-domain.auth0.com
   AUTH0_API_AUDIENCE=your-api-identifier
   OPENTRIPMAP_API_KEY=your-opentripmap-api-key
   OPENROUTESERVICE_API_KEY=your-openrouteservice-api-key
   AMADEUS_API_KEY=your-amadeus-api-key
   AMADEUS_API_SECRET=your-amadeus-api-secret
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

   Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_AUTH0_DOMAIN=your-auth0-domain.auth0.com
   NEXT_PUBLIC_AUTH0_CLIENT_ID=your-auth0-client-id
   NEXT_PUBLIC_AUTH0_AUDIENCE=your-api-identifier
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

### Running the Application

Start the backend:
```bash
cd backend
python run.py
```
This runs on `http://localhost:5000`

Start the frontend:
```bash
cd frontend
npm run dev
```
This runs on `http://localhost:3000`

Open `http://localhost:3000` in your browser.

## Project Structure

```
KORA/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangChain AI agent implementation
│   │   │   ├── agent_executor.py
│   │   │   └── tools.py
│   │   ├── api/            # API routes and authentication
│   │   │   ├── auth.py
│   │   │   └── routes.py
│   │   ├── models/         # Database models
│   │   │   ├── user.py
│   │   │   └── itinerary.py
│   │   └── services/       # Business logic services
│   │       ├── carbon_calculator.py
│   │       ├── flight_api.py
│   │       └── travel_data_api.py
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   └── run.py             # Application entry point
│
└── frontend/
    ├── src/
    │   ├── app/            # Next.js app router pages
    │   │   ├── chat/       # AI chat interface
    │   │   ├── globe/      # 3D globe visualization
    │   │   ├── profile/    # User profile page
    │   │   └── result/     # Trip results page
    │   ├── components/     # React components
    │   │   ├── Globe.tsx
    │   │   ├── CarbonVisualization.tsx
    │   │   └── TravelModal.tsx
    │   └── contexts/       # React contexts
    │       └── AuthContext.tsx
    ├── public/             # Static assets
    └── package.json       # Node.js dependencies
```

## Features

- Interactive 3D globe to visualize travel destinations
- AI-powered chat interface for trip planning
- Carbon footprint calculations with visual representations
- City and landmark recommendations from the AI
- User profiles to track travel history and carbon footprint
- Auth0 authentication

## Design Philosophy

We wanted to make sustainability feel approachable, not intimidating. The UI is designed to be friendly and welcoming. Our mascot Kora (a turtle) represents the environmental and oceanic inspiration behind the project. The goal is to reframe carbon footprint discussions from something scary into something that can actually be rewarding.

## Challenges We Faced

The main challenge was building a UI that doesn't overwhelm users. Carbon footprint discussions can feel heavy, so we focused on making the experience fun and straightforward. We ended up with a design that guides users naturally through the planning process without making them feel guilty or anxious.

## What We Learned

Working with LangChain was interesting. The agents add a lot of functionality, but you need to be really specific with your prompts or the output gets messy. We also learned a lot about building AI agents and creating interfaces that make complex environmental data accessible.

## Future Plans

We're planning to add:
- A friends feature with a leaderboard to track progress
- Gamification elements to encourage friendly competition
- Long-term carbon footprint tracking to help users see their impact over time
- More UX improvements as we continue iterating

## Contributing

Contributions are welcome. Feel free to open a pull request.
