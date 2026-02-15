import React, { useEffect, useState } from 'react';
import {
    IonContent, IonPage, IonGrid, IonRow, IonCol, IonCard, IonCardContent, IonCardHeader, IonCardSubtitle, IonCardTitle,
    IonList, IonItem, IonLabel, IonNote, IonIcon, IonBadge
} from '@ionic/react';
import { statsChartOutline, peopleOutline, gitNetworkOutline } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import api from '../api';
import './AdminDashboard.css';

const AdminDashboard: React.FC = () => {
    const history = useHistory();
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const res = await api.get('/stats');
            setStats(res.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <IonPage className="admin-page">


            <IonContent className="ion-padding">
                {loading ? (
                    <div className="loading-state">Loading Analytics...</div>
                ) : stats && (
                    <div className="admin-content">
                        <h1 className="page-title">System Administration</h1>
                        {/* Summary Cards */}
                        <IonGrid>
                            <IonRow>
                                <IonCol size="12" sizeMd="4">
                                    <IonCard className="stat-card">
                                        <IonCardHeader>
                                            <IonCardSubtitle>Total Visits</IonCardSubtitle>
                                            <IonCardTitle>{stats.total_visits}</IonCardTitle>
                                        </IonCardHeader>
                                        <IonIcon icon={peopleOutline} className="stat-icon" />
                                    </IonCard>
                                </IonCol>
                                <IonCol size="12" sizeMd="4">
                                    <IonCard className="stat-card">
                                        <IonCardHeader>
                                            <IonCardSubtitle>Departments Active</IonCardSubtitle>
                                            <IonCardTitle>{Object.keys(stats.department_load).length}</IonCardTitle>
                                        </IonCardHeader>
                                        <IonIcon icon={gitNetworkOutline} className="stat-icon" />
                                    </IonCard>
                                </IonCol>
                                <IonCol size="12" sizeMd="4">
                                    <IonCard className="stat-card">
                                        <IonCardHeader>
                                            <IonCardSubtitle>High Risk Cases</IonCardSubtitle>
                                            <IonCardTitle>{stats.risk_distribution['High'] || 0}</IonCardTitle>
                                        </IonCardHeader>
                                        <IonIcon icon={statsChartOutline} className="stat-icon" />
                                    </IonCard>
                                </IonCol>
                            </IonRow>
                        </IonGrid>

                        {/* Recent Activity */}
                        <div className="section-header">
                            <h3>Recent Visits</h3>
                        </div>
                        <IonList>
                            {stats.recent_visits.map((v: any) => (
                                <IonItem key={v.visit_id}>
                                    <IonLabel>
                                        <h2>Status: {v.status}</h2>
                                        <p>{new Date(v.arrival_time).toLocaleString()}</p>
                                    </IonLabel>
                                    <IonNote slot="end" color="primary">{v.age}y / {v.gender}</IonNote>
                                </IonItem>
                            ))}
                        </IonList>

                        {/* Department Load */}
                        <div className="section-header" style={{ marginTop: '2rem' }}>
                            <h3>Department Load</h3>
                        </div>
                        <IonGrid>
                            <IonRow>
                                {Object.entries(stats.department_load).map(([dept, count]: any) => (
                                    <IonCol size="6" sizeMd="3" key={dept}>
                                        <IonCard className="dept-card">
                                            <IonCardContent>
                                                <h2>{dept}</h2>
                                                <div className="dept-count">{count}</div>
                                                <p>Pending</p>
                                            </IonCardContent>
                                        </IonCard>
                                    </IonCol>
                                ))}
                            </IonRow>
                        </IonGrid>
                    </div>
                )}
            </IonContent>
        </IonPage>
    );
};

export default AdminDashboard;
