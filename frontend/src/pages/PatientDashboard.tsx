import React, { useEffect, useState } from 'react';
import {
    IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonButton,
    IonCard, IonCardContent, IonCardHeader, IonCardTitle,
    IonNote, IonIcon, IonBadge, IonGrid, IonRow, IonCol
} from '@ionic/react';
import { personOutline, timeOutline, logOutOutline } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import api from '../api';
import './PatientDashboard.css';

const PatientDashboard: React.FC = () => {
    const history = useHistory();
    const [profile, setProfile] = useState<any>(null);
    const [visits, setVisits] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchRecords();
    }, []);

    const fetchRecords = async () => {
        try {
            const res = await api.get('/patient/my-records');
            if (res.data.status === 'no_record') {
                setError(res.data.message);
            } else {
                setProfile(res.data.patient);
                setVisits(res.data.visits);
            }
        } catch (err: any) {
            console.error(err);
            if (err.response?.status === 403) {
                setError("Authorized for Patients only.");
            } else {
                setError("Failed to load records.");
            }
        } finally {
            setLoading(false);
        }
    };

    const getRiskColor = (level: string) => {
        switch (level) {
            case 'High': return 'danger';
            case 'Medium': return 'warning';
            default: return 'success';
        }
    };

    return (
        <IonPage className="patient-page">
            <IonHeader>
                <IonToolbar color="success">
                    <IonTitle>My Health Portal</IonTitle>
                    <IonButtons slot="end">
                        <IonButton onClick={() => {
                            localStorage.clear();
                            history.replace('/login');
                        }}>
                            <IonIcon icon={logOutOutline} />
                        </IonButton>
                    </IonButtons>
                </IonToolbar>
            </IonHeader>

            <IonContent className="ion-padding">
                {loading ? (
                    <div className="center-msg">Loading your health data...</div>
                ) : error ? (
                    <div className="center-msg error">{error}</div>
                ) : (
                    <div className="dashboard-container">
                        <IonCard className="profile-card">
                            <IonCardContent>
                                <div className="profile-header">
                                    <div className="avatar-circle">
                                        <IonIcon icon={personOutline} />
                                    </div>
                                    <div className="profile-text">
                                        <h2>{profile.full_name}</h2>
                                        <p>{profile.gender}, {profile.age} years old</p>
                                        <IonBadge color="medium">BP: {profile.blood_pressure}</IonBadge>
                                        {profile.symptoms && (
                                            <IonNote className="profile-symptoms">Symptoms: {profile.symptoms}</IonNote>
                                        )}
                                        {profile.pre_existing_conditions && (
                                            <IonNote className="profile-symptoms">
                                                Conditions: {profile.pre_existing_conditions}
                                            </IonNote>
                                        )}
                                    </div>
                                </div>
                            </IonCardContent>
                        </IonCard>

                        <IonGrid className="stats-grid">
                            <IonRow>
                                <IonCol size="6">
                                    <IonCard className="stat-card blue">
                                        <IonCardContent>
                                            <div className="stat-value">{visits.length}</div>
                                            <div className="stat-label">Total Visits</div>
                                        </IonCardContent>
                                    </IonCard>
                                </IonCol>
                                <IonCol size="6">
                                    <IonCard className="stat-card purple">
                                        <IonCardContent>
                                            <div className="stat-value">
                                                {visits.length > 0 ? (visits.reduce((acc, v) => acc + (v.risk_score || 0), 0) / visits.length).toFixed(1) : 0}
                                            </div>
                                            <div className="stat-label">Avg. Risk Score</div>
                                        </IonCardContent>
                                    </IonCard>
                                </IonCol>
                            </IonRow>
                        </IonGrid>

                        <h3 className="section-title">Visit History</h3>

                        {visits.length === 0 ? (
                            <div className="empty-visits">No visits recorded.</div>
                        ) : (
                            <div className="visits-list">
                                {visits.map((visit) => (
                                    <IonCard key={visit.visit_id} className="visit-card">
                                        <IonCardHeader>
                                            <div className="visit-header-row">
                                                <IonNote>{new Date(visit.arrival_time).toLocaleDateString()}</IonNote>
                                                <IonBadge color={getRiskColor(visit.risk_level)}>{visit.risk_level}</IonBadge>
                                            </div>
                                            <IonCardTitle>{visit.dept} Department</IonCardTitle>
                                        </IonCardHeader>
                                        <IonCardContent>
                                            <div className="visit-detail-row">
                                                <span><IonIcon icon={timeOutline} /> {new Date(visit.arrival_time).toLocaleTimeString()}</span>
                                                <IonBadge color="light" mode="ios">{visit.status}</IonBadge>
                                            </div>
                                            <div className="visit-score-container">
                                                <div className="score-bar">
                                                    <div className="score-fill" style={{ width: `${(visit.risk_score || 0) * 10}%`, background: getRiskColor(visit.risk_level) === 'danger' ? '#eb445a' : '#2dd36f' }}></div>
                                                </div>
                                                <span className="score-text">AI Risk Score: {visit.risk_score}/10</span>
                                            </div>
                                        </IonCardContent>
                                    </IonCard>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </IonContent>
        </IonPage>
    );
};

export default PatientDashboard;
