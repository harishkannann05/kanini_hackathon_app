import React, { useState, useEffect } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { IonIcon } from '@ionic/react';
import {
    logInOutline,
    logOutOutline,
    menuOutline,
    closeOutline,
    homeOutline,
    clipboardOutline,
    statsChartOutline,
    peopleOutline
} from 'ionicons/icons';
import medicyLogo from '../assets/medicy_logo.png';
import './Navbar.css';

const Navbar: React.FC = () => {
    const history = useHistory();
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);

    // Handle scroll effect
    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    // Close mobile menu on route change
    useEffect(() => {
        setMobileMenuOpen(false);
    }, [location]);

    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');

    const getDashboardPath = () => {
        if (!role) return '/dashboard';
        switch (role) {
            case 'Admin': return '/admin-dashboard';
            case 'Doctor': return '/doctor-dashboard';
            case 'Recipient': return '/recipient-dashboard';
            case 'Patient': return '/patient-dashboard';
            default: return '/dashboard';
        }
    };

    const navItems = [
        { path: '/', label: 'Home', icon: homeOutline, show: 'always' },
        { path: '/intake', label: 'Patient Intake', icon: clipboardOutline, show: 'always' },
        { path: '/doctors', label: 'Doctors', icon: peopleOutline, show: 'always' },
        { path: getDashboardPath(), label: 'Dashboard', icon: statsChartOutline, show: 'authed' },
        { path: '/login', label: 'Login', icon: logInOutline, show: 'unauthed' },
        { path: 'logout', label: 'Logout', icon: logOutOutline, show: 'authed' },
    ];

    const filteredItems = navItems.filter(item => {
        if (item.show === 'always') return true;
        if (item.show === 'authed') return !!token;
        if (item.show === 'unauthed') return !token;
        return true;
    });

    const isActive = (path: string) => {
        return location.pathname === path;
    };

    const handleNavigation = (path: string) => {
        if (path === 'logout') {
            localStorage.clear();
            history.push('/login');
        } else {
            history.push(path);
        }
        setMobileMenuOpen(false);
    };

    return (
        <>
            <nav className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}>
                <div className="navbar-container">
                    {/* Logo */}
                    <div className="navbar-brand" onClick={() => history.push('/')}>
                        <div className="brand-logo-wrapper">
                            <img src={medicyLogo} alt="Medicy" className="brand-logo-img" />
                        </div>
                        <span className="brand-text">Medicy</span>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="navbar-menu desktop-menu">
                        {filteredItems.map((item) => (
                            <button
                                key={item.path}
                                className={`nav-item ${isActive(item.path) ? 'nav-item-active' : ''}`}
                                onClick={() => handleNavigation(item.path)}
                            >
                                <IonIcon icon={item.icon} className="nav-icon" />
                                <span>{item.label}</span>
                            </button>
                        ))}
                    </div>

                    {/* Mobile Menu Toggle */}
                    <button
                        className="mobile-menu-toggle"
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        aria-label="Toggle menu"
                    >
                        <IonIcon icon={mobileMenuOpen ? closeOutline : menuOutline} />
                    </button>
                </div>

                {/* Mobile Navigation */}
                <div className={`mobile-menu ${mobileMenuOpen ? 'mobile-menu-open' : ''}`}>
                    <div className="mobile-menu-content">
                        {filteredItems.map((item) => (
                            <button
                                key={item.path}
                                className={`mobile-nav-item ${isActive(item.path) ? 'mobile-nav-item-active' : ''}`}
                                onClick={() => handleNavigation(item.path)}
                            >
                                <IonIcon icon={item.icon} className="mobile-nav-icon" />
                                <span>{item.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </nav>

            {/* Mobile Menu Overlay */}
            {mobileMenuOpen && (
                <div
                    className="mobile-menu-overlay"
                    onClick={() => setMobileMenuOpen(false)}
                />
            )}
        </>
    );
};

export default Navbar;
