import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

export default function Layout() {
    const [mobileOpen, setMobileOpen] = useState(false);

    return (
        <div className="app-shell">
            <Sidebar
                mobileOpen={mobileOpen}
                onClose={() => setMobileOpen(false)}
            />

            {mobileOpen && (
                <div
                    className="sidebar-overlay"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            <main className="main-area">
                <Topbar onMenu={() => setMobileOpen(true)} />

                <div className="page-content">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}