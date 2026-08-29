import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

import Overview from "./pages/Overview";
import WeatherAnalysis from "./pages/WeatherAnalysis";
import QueryTool from "./pages/QueryTool";
import BatchLogs from "./pages/BatchLogs";

import { Routes, Route } from "react-router-dom";

import "./styles/main.scss";


function App() {

    return (
        <div className="app">

            <Sidebar />

            <div className="app__main">

                <Header />

                <main className="app__content">

                    <Routes>

                        <Route
                            path="/"
                            element={<Overview />}
                        />

                        <Route
                            path="/weather"
                            element={<WeatherAnalysis />}
                        />

                        <Route
                            path="/query"
                            element={<QueryTool />}
                        />

                        <Route
                            path="/batch-logs"
                            element={<BatchLogs />}
                        />

                    </Routes>

                </main>

            </div>

        </div>
    );
}

export default App;