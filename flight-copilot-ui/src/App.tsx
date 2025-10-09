import { Routes, Route, NavLink, Navigate } from 'react-router-dom';
import FlightSearchPage from './pages/FlightSearchPage';
import AIGeneratePage from './pages/AIGeneratePage';

const tabBase = 'px-4 py-2 rounded-lg text-sm font-medium transition-colors';
const tabActive = 'bg-blue-600 text-white';
const tabIdle = 'bg-slate-100 text-slate-700 hover:bg-slate-200';

const App = () => {
  return (
    <div className="p-6 space-y-4 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-800">Flight Copilot</h1>

      <div className="flex gap-2">
        <NavLink
          to="/search"
          className={({ isActive }) =>
            `${tabBase} ${isActive ? tabActive : tabIdle}`
          }
        >
          Search flights
        </NavLink>

        <NavLink
          to="/ai"
          className={({ isActive }) =>
            `${tabBase} ${isActive ? tabActive : tabIdle}`
          }
        >
          AI generate
        </NavLink>
      </div>

      <Routes>
        <Route path="/" element={<Navigate to="/search" replace />} />
        <Route path="/search" element={<FlightSearchPage />} />
        <Route path="/ai" element={<AIGeneratePage />} />
        <Route path="*" element={<Navigate to="/search" replace />} />
      </Routes>
    </div>
  );
};

export default App;
