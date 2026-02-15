import React, { useEffect, useState } from 'react';
import { IonContent, IonPage, IonGrid, IonRow, IonCol, IonCard, IonCardHeader, IonCardSubtitle, IonCardTitle, IonCardContent, IonButton, IonBadge, IonList, IonItem, IonLabel } from '@ionic/react';
import api from '../api';

import { useHistory } from 'react-router-dom';
import './Dashboard.css';

const Dashboard: React.FC = () => {
    const history = useHistory();
    const [stats, setStats] = useState<any>(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await api.get('/stats');
                setStats(res.data);
            } catch (error) {
                console.error("Failed to fetch stats", error);
            }
        };
        fetchStats();
        const interval = setInterval(fetchStats, 5000);
        return () => clearInterval(interval);
    }, []);

    if (!stats) return <div className="loading-container">Loading hospital stats...</div>;

    return (
        <IonPage className="dashboard-page">

            <IonContent className="dark-content">
                <div className="dashboard-container">
                    <IonGrid>
                        <IonRow>
                            <IonCol size="12" sizeMd="4">
                                <IonCard className="summary-card">
                                    <IonCardHeader>
                                        <IonCardSubtitle className="stat-label">Total Visits</IonCardSubtitle>
                                        <IonCardTitle className="stat-value">{stats.total_visits}</IonCardTitle>
                                    </IonCardHeader>
                                </IonCard>
                            </IonCol>
                            <IonCol size="12" sizeMd="4">
                                <IonCard className="summary-card high-risk-card">
                                    <IonCardHeader>
                                        <IonCardSubtitle className="stat-label">High Risk Alerts</IonCardSubtitle>
                                        <IonCardTitle className="stat-value" style={{ color: '#ff4757' }}>
                                            {stats.risk_distribution?.High || 0}
                                        </IonCardTitle>
                                    </IonCardHeader>
                                </IonCard>
                            </IonCol>
                            <IonCol size="12" sizeMd="4">
                                <IonCard className="summary-card waiting-card">
                                    <IonCardHeader>
                                        <IonCardSubtitle className="stat-label">Currently Waiting</IonCardSubtitle>
                                        <IonCardTitle className="stat-value" style={{ color: '#ffa502' }}>
                                            {Number(Object.values(stats.department_load || {}).reduce((a: any, b: any) => a + b, 0))}
                                        </IonCardTitle>
                                    </IonCardHeader>
                                </IonCard>
                            </IonCol>
                        </IonRow>

                        <IonRow style={{ marginTop: '2rem' }}>
                            <IonCol size="12" sizeMd="6">
                                <IonCard className="content-card">
                                    <IonCardHeader>
                                        <IonCardTitle className="card-title">Department Load</IonCardTitle>
                                    </IonCardHeader>
                                    <IonCardContent>
                                        <IonList className="dark-list">
                                            {Object.entries(stats.department_load || {}).sort((a, b) => (b[1] as any) - (a[1] as any)).map(([dept, count]: any) => (
                                                <IonItem key={dept} className="dark-item">
                                                    <IonLabel>{dept}</IonLabel>
                                                    <IonBadge slot="end" color={count > 5 ? 'danger' : 'success'}>
                                                        {count as number} patients
                                                    </IonBadge>
                                                </IonItem>
                                            ))}
                                        </IonList>
                                    </IonCardContent>
                                </IonCard>
                            </IonCol>

                            <IonCol size="12" sizeMd="6">
                                <IonCard className="content-card">
                                    <IonCardHeader>
                                        <IonCardTitle className="card-title">Recent Triage Activity</IonCardTitle>
                                    </IonCardHeader>
                                    <IonCardContent>
                                        <IonList className="dark-list">
                                            {stats.recent_visits?.map((visit: any) => (
                                                <IonItem key={visit.visit_id} className="dark-item">
                                                    <IonLabel>
                                                        <h2>Patient ({visit.gender}, Age: {visit.age})</h2>
                                                        <p>Arrived: {new Date(visit.arrival_time).toLocaleTimeString()}</p>
                                                    </IonLabel>
                                                    <IonBadge slot="end" color={visit.status === 'Completed' ? 'success' : 'warning'}>
                                                        {visit.status}
                                                    </IonBadge>
                                                </IonItem>
                                            ))}
                                        </IonList>
                                    </IonCardContent>
                                </IonCard>
                            </IonCol>
                        </IonRow>
                    </IonGrid>

                    <div className="action-buttons">
                        <IonButton className="primary-btn" onClick={() => history.push('/intake')}>
                            New Intake Form
                        </IonButton>
                        <IonButton fill="outline" className="secondary-btn" onClick={() => history.push('/doctors')}>
                            Manage Staff
                        </IonButton>
                    </div>
                </div>
            </IonContent>
        </IonPage>
    );
};

export default Dashboard;
