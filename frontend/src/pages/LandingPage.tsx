import React, { useState } from 'react';
import {
    IonContent, IonPage, IonIcon, IonGrid, IonRow, IonCol
} from '@ionic/react';
import {
    pulseOutline,
    timerOutline,
    peopleOutline,
    arrowForward,
    calendarOutline,
    videocamOutline,
    medkitOutline,
    searchOutline,
    locationOutline,
    chevronForward,
    callOutline,
    mailOutline,
    logoFacebook,
    logoTwitter,
    logoInstagram
} from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import medicyLogo from '../assets/medicy_logo.png';
import './LandingPage.css';

const LandingPage: React.FC = () => {
    const history = useHistory();
    const [searchText, setSearchText] = useState('');

    const quickActions = [
        { title: 'Book Appointment', icon: calendarOutline, color: 'orange', path: '/intake' },
        { title: 'Video Consult', icon: videocamOutline, color: 'blue', path: '/intake' },
        { title: 'Buy Medicines', icon: medkitOutline, color: 'green', path: '/dashboard' },
        { title: 'Find Hospitals', icon: locationOutline, color: 'teal', path: '/dashboard' },
    ];

    return (
        <IonPage className="landing-page">
            <IonContent fullscreen className="landing-content">
                {/* Hero Section */}
                <div className="hero-section">
                    <div className="hero-content">
                        <div className="hero-text-container">
                            <div className="hero-logo-wrapper">
                                <img src={medicyLogo} alt="Medicy Healthcare" className="hero-logo" />
                                <span className="hero-brand-name">Medicy</span>
                            </div>
                            <h1 className="hero-title">
                                Advanced Care,<br />
                                <span className="highlight-text">Always There.</span>
                            </h1>
                            <p className="hero-subtitle">
                                Experience world-class medical excellence with our AI-powered triage and appointment system.
                            </p>

                            {/* Search Bar */}
                            <div className="hero-search-container">
                                <div className="search-box">
                                    <IonIcon icon={searchOutline} className="search-icon" />
                                    <input
                                        type="text"
                                        placeholder="Search doctors, specialties, or symptoms..."
                                        value={searchText}
                                        onChange={e => setSearchText(e.target.value)}
                                    />
                                    <button className="search-btn">
                                        <IonIcon icon={arrowForward} />
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Quick Actions Cards */}
                        <div className="quick-actions-grid">
                            {quickActions.map((action, index) => (
                                <div
                                    key={index}
                                    className={`action-card ${action.color}`}
                                    onClick={() => history.push(action.path)}
                                >
                                    <div className="action-icon-wrapper">
                                        <IonIcon icon={action.icon} />
                                    </div>
                                    <h3>{action.title}</h3>
                                    <IonIcon icon={chevronForward} className="arrow-icon" />
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Statistics / Trust Section */}
                <div className="stats-section">
                    <div className="stat-item">
                        <span className="stat-number">10k+</span>
                        <span className="stat-label">Doctors</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-number">50+</span>
                        <span className="stat-label">Hospitals</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-number">24/7</span>
                        <span className="stat-label">Emergency</span>
                    </div>
                </div>

                {/* Features Section */}
                <div className="features-section">
                    <div className="section-header-center">
                        <h2>Centers of Excellence</h2>
                        <p>Specialized care for every medical need</p>
                    </div>
                    <IonGrid>
                        <IonRow>
                            <IonCol size="12" sizeMd="4">
                                <div className="feature-card">
                                    <div className="icon-box blue">
                                        <IonIcon icon={pulseOutline} />
                                    </div>
                                    <h3>Cardiology</h3>
                                    <p>Comprehensive heart care with advanced diagnostic and treatment technologies.</p>
                                    <span className="learn-more">Learn more <IonIcon icon={arrowForward} /></span>
                                </div>
                            </IonCol>
                            <IonCol size="12" sizeMd="4">
                                <div className="feature-card">
                                    <div className="icon-box purple">
                                        <IonIcon icon={timerOutline} />
                                    </div>
                                    <h3>Emergency Care</h3>
                                    <p>Round-the-clock emergency services with rapid response teams and AI triage.</p>
                                    <span className="learn-more">Learn more <IonIcon icon={arrowForward} /></span>
                                </div>
                            </IonCol>
                            <IonCol size="12" sizeMd="4">
                                <div className="feature-card">
                                    <div className="icon-box green">
                                        <IonIcon icon={peopleOutline} />
                                    </div>
                                    <h3>Neurology</h3>
                                    <p>Expert care for neurological disorders with a multidisciplinary approach.</p>
                                    <span className="learn-more">Learn more <IonIcon icon={arrowForward} /></span>
                                </div>
                            </IonCol>
                        </IonRow>
                    </IonGrid>
                </div>

                {/* Footer Section */}
                <footer className="landing-footer">
                    <div className="footer-content">
                        <div className="footer-brand">
                            <div className="footer-logo">
                                <img src={medicyLogo} alt="Medicy" />
                                <span>Medicy</span>
                            </div>
                            <p>Transforming healthcare with AI-powered triage and seamless patient management.</p>
                            <div className="social-links">
                                <a href="#"><IonIcon icon={logoFacebook} /></a>
                                <a href="#"><IonIcon icon={logoTwitter} /></a>
                                <a href="#"><IonIcon icon={logoInstagram} /></a>
                            </div>
                        </div>

                        <div className="footer-links">
                            <h3>Quick Links</h3>
                            <ul>
                                <li><a href="#">About Us</a></li>
                                <li><a href="#">Our Doctors</a></li>
                                <li><a href="#">Departments</a></li>
                                <li><a href="#">Book Appointment</a></li>
                            </ul>
                        </div>

                        <div className="footer-contact">
                            <h3>Contact Us</h3>
                            <div className="contact-item">
                                <IonIcon icon={locationOutline} />
                                <span>123 Medical Center Dr,<br />Healthcare City, HC 90210</span>
                            </div>
                            <div className="contact-item">
                                <IonIcon icon={callOutline} />
                                <span>+1 (555) 123-4567</span>
                            </div>
                            <div className="contact-item">
                                <IonIcon icon={mailOutline} />
                                <span>support@medicy.com</span>
                            </div>
                        </div>
                    </div>
                    <div className="footer-bottom">
                        <p>&copy; {new Date().getFullYear()} Medicy Healthcare. All rights reserved.</p>
                    </div>
                </footer>
            </IonContent>
        </IonPage>
    );
};

export default LandingPage;
