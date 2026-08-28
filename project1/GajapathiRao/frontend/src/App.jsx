import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Dashboard from "./pages/Dashboard";

import "./styles/main.scss";

function App() {
    return (
        <div className="app">

            <Sidebar />

            <div className="app__main">

                <Header />

                <Dashboard />

            </div>

        </div>
    );
}

export default App;