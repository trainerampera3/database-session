import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

import Overview from "./pages/Overview";
import WeatherAnalysis from "./pages/WeatherAnalysis";
import QueryTool from "./pages/QueryTool";
import BatchLogs from "./pages/BatchLogs";
import HourlyWeather from "./pages/HourlyWeather";
import News from "./pages/News";
import ETLPage from "./pages/EtlPage";
import LogIn from "./pages/LogIn";
import Register from "./pages/Register";

import "./styles/global.scss";


const ProtectedRoute = ({ children }) => {
    const isAuthenticated = localStorage.getItem("auth_token");
    return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const AuthRoute = ({ children }) => {
    const isAuthenticated = localStorage.getItem("auth_token");
    return !isAuthenticated ? children : <Navigate to="/" replace />;
};

function App() {
    const location = useLocation();
    
    const isAuthPage = ["/login", "/register"].includes(location.pathname.toLowerCase());

    return (
        <div className="app">
           
            {!isAuthPage && <Sidebar />}

            <div className={isAuthPage ? "app__auth" : "app__main"}>
                {!isAuthPage && <Header />}

                <main className={isAuthPage ? "auth__content" : "app__content"}>
                    <Routes>
                      
                        <Route path="/" element={<ProtectedRoute><Overview /></ProtectedRoute>} />
                        <Route path="/hourly-weather" element={<ProtectedRoute><HourlyWeather /></ProtectedRoute>} />
                        <Route path="/etl-page" element={<ProtectedRoute><ETLPage /></ProtectedRoute>} />
                        <Route path="/weather" element={<ProtectedRoute><WeatherAnalysis /></ProtectedRoute>} />
                        <Route path="/query" element={<ProtectedRoute><QueryTool /></ProtectedRoute>} />
                        <Route path="/batch-logs" element={<ProtectedRoute><BatchLogs /></ProtectedRoute>} />
                        <Route path="/news" element={<ProtectedRoute><News /></ProtectedRoute>} />

                        <Route path="/login" element={<AuthRoute><LogIn /></AuthRoute>} />
                        <Route path="/register" element={<AuthRoute><Register /></AuthRoute>} />
                        
                        
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </main>
            </div>
        </div>
    );
}

export default App;
