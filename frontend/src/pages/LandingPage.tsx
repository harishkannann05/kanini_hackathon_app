import React from 'react';
import { IonContent, IonPage, IonButton, IonIcon, IonGrid, IonRow, IonCol } from '@ionic/react';
import { pulseOutline, timerOutline, peopleOutline, arrowForward } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import './LandingPage.css';

const LandingPage: React.FC = () => {
    const history = useHistory();

    return (
        <IonPage className="landing-page">
            <IonContent fullscreen className="landing-content">
                <div className="hero-section">
                    <div className="hero-content">
                        <div className="badge">AI-POWERED HEALTHCARE</div>
                        <h1 className="hero-title">
                            Smart Patient <span className="gradient-text">Triage System</span>
                        </h1>
                        <p className="hero-subtitle">
                            Revolutionizing emergency room efficiency with real-time AI assessment,
                            dynamic doctor allocation, and accurate wait-time prediction.
                        </p>
                        <div className="cta-container">
                            <IonButton
                                className="primary-cta"
                                onClick={() => history.push('/intake')}
                            >
                                Start New Triage <IonIcon icon={arrowForward} slot="end" />
                            </IonButton>
                            <IonButton
                                fill="outline"
                                className="secondary-cta"
                                onClick={() => history.push('/dashboard')}
                            >
                                View Dashboard
                            </IonButton>
                        </div>
                    </div>
                </div>

                <div className="features-section">
                    <IonGrid>
                        <IonRow>
                            <IonCol size="12" sizeMd="4">
                                <div className="feature-card">
                                    <div className="icon-box blue">
                                        <IonIcon icon={pulseOutline} />
                                    </div>
                                    <h3>AI Risk Assessment</h3>
                                    <p>Instantly analyzes symptoms and vitals to determine risk levels and prioritize critical cases automatically.</p>
                                </div>
                            </IonCol>
                            <IonCol size="12" sizeMd="4">
                                <div className="feature-card">
                                    <div className="icon-box purple">
                                        <IonIcon icon={timerOutline} />
                                    </div>
                                    <h3>Smart Wait Times</h3>
                                    <p>Dynamic algorithms predict accurate wait times based on doctor availability and current department load.</p>
                                </div>
                            </IonCol>
                            <IonCol size="12" sizeMd="4">
                                <div className="feature-card">
                                    <div className="icon-box green">
                                        <IonIcon icon={peopleOutline} />
                                    </div>
                                    <h3>Resource Optimization</h3>
                                    <p>Efficiently allocates medical staff to departments with high demand, reducing improved patient throughput.</p>
                                </div>
                            </IonCol>
                        </IonRow>
                    </IonGrid>
                </div>
            </IonContent>
        </IonPage>
    );
};

export default LandingPage;
