import { Link, useLocation } from "react-router-dom"
import "./index.scss"

export default function PageSelector() {
    const location = useLocation();
    return (
        <div className="page-selector">
            <Link to="/jsp">
                <button className={`page-selector-button ${location.pathname === "/jsp" ? "active" : ""}`}></button>
            </Link>
            <Link to="/">
                <button className={`page-selector-button ${location.pathname === "/" ? "active" : ""}`}></button>
            </Link>
            <Link to="/settings">
                <button className={`page-selector-button ${location.pathname === "/settings" ? "active" : ""}`}></button>
            </Link>
        </div>
    )
}
