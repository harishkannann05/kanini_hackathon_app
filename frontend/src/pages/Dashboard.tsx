import React, { useState, useEffect } from 'react';
import {
    IonContent, IonPage, IonGrid, IonRow, IonCol, IonCard,
    IonCardContent, IonCardHeader, IonCardSubtitle, IonCardTitle,
    IonIcon, IonProgressBar, IonText, IonButton
} from '@ionic/react';
import {
    peopleOutline,
    medkitOutline,
    pulseOutline,
    timeOutline,
    warningOutline,
    checkmarkCircleOutline,
    arrowForward,
    statsChartOutline
} from 'ionicons/icons';
import api from '../api';
import './Dashboard.css';

const Dashboard: React.FC = () => {
    const [stats, setStats] = useState({
        total_visits: 1240,
        avg_wait_time: 15, // minutes
        critical_cases: 3,
        doctors_active: 8
    });

    // Mock Department Data for Visualization
    const departments = [
        { name: 'General Medicine', capacity: 0.8, patients: 45, max: 50 },
        { name: 'Cardiology', capacity: 0.4, patients: 12, max: 30 },
        { name: 'Pediatrics', capacity: 0.6, patients: 24, max: 40 },
        { name: 'Orthopedics', capacity: 0.2, patients: 5, max: 25 },
        { name: 'Emergency', capacity: 0.9, patients: 18, max: 20 },
    ];

    const activities = [
        { time: '10:30 AM', msg: 'Dr. Sarah completed triage for Patient #1024', type: 'success' },
        { time: '10:15 AM', msg: 'New critical patient admitted to ER', type: 'critical' },
        { time: '09:45 AM', msg: 'System maintenance scheduled for tonight', type: 'info' },
    ];

    return (
        <IonPage className="dashboard-page">
            <IonContent fullscreen className="dashboard-content">
                <div className="dashboard-container">

                    {/* Welcome Section */}
                    <div className="welcome-banner">
                        <div className="welcome-text">
                            <h1>Hospital Overview</h1>
                            <p>Real-time analytics and department status.</p>
                        </div>
                        <div className="date-badge">
                            <IonIcon icon={timeOutline} />
                            <span>{new Date().toLocaleDateString()}</span>
                        </div>
                    </div>

                    {/* Key Metrics Grid */}
                    <IonGrid className="metrics-grid">
                        <IonRow>
                            <IonCol size="12" sizeSm="6" sizeMd="3">
                                <div className="metric-card blue">
                                    <div className="icon-wrapper">
                                        <IonIcon icon={peopleOutline} />
                                    </div>
                                    <div className="metric-content">
                                        <h3>{stats.total_visits}</h3>
                                        <p>Total Visits</p>
                                    </div>
                                    <div className="trend up">
                                        <IonIcon icon={statsChartOutline} /> +12%
                                    </div>
                                </div>
                            </IonCol>
                            <IonCol size="12" sizeSm="6" sizeMd="3">
                                <div className="metric-card orange">
                                    <div className="icon-wrapper">
                                        <IonIcon icon={timeOutline} />
                                    </div>
                                    <div className="metric-content">
                                        <h3>{stats.avg_wait_time}m</h3>
                                        <p>Avg Wait Time</p>
                                    </div>
                                    <div className="trend down">
                                        <IonIcon icon={statsChartOutline} /> -5%
                                    </div>
                                </div>
                            </IonCol>
                            <IonCol size="12" sizeSm="6" sizeMd="3">
                                <div className="metric-card red">
                                    <div className="icon-wrapper">
                                        <IonIcon icon={pulseOutline} />
                                    </div>
                                    <div className="metric-content">
                                        <h3>{stats.critical_cases}</h3>
                                        <p>Critical Cases</p>
                                    </div>
                                    <div className="trend">Active</div>
                                </div>
                            </IonCol>
                            <IonCol size="12" sizeSm="6" sizeMd="3">
                                <div className="metric-card teal">
                                    <div className="icon-wrapper">
                                        <IonIcon icon={medkitOutline} />
                                    </div>
                                    <div className="metric-content">
                                        <h3>{stats.doctors_active}</h3>
                                        <p>Doctors Online</p>
                                    </div>
                                    <div className="trend">Full Staff</div>
                                </div>
                            </IonCol>
                        </IonRow>
                    </IonGrid>

                    {/* Main Content Split: Departments & Activity */}
                    <IonGrid>
                        <IonRow>
                            {/* Department Load */}
                            <IonCol size="12" sizeLg="8">
                                <div className="content-card">
                                    <div className="card-header">
                                        <h3>Department Capacity</h3>
                                        <IonButton fill="clear" size="small">View All</IonButton>
                                    </div>
                                    <div className="dept-list">
                                        {departments.map((dept, i) => (
                                            <div key={i} className="dept-item">
                                                <div className="dept-info">
                                                    <span className="dept-name">{dept.name}</span>
                                                    <span className="dept-stats">{dept.patients} / {dept.max}</span>
                                                </div>
                                                <IonProgressBar
                                                    value={dept.capacity}
                                                    color={dept.capacity > 0.8 ? 'danger' : (dept.capacity > 0.5 ? 'warning' : 'primary')}
                                                    className="dept-progress"
                                                />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </IonCol>

                            {/* Recent Activity */}
                            <IonCol size="12" sizeLg="4">
                                <div className="content-card">
                                    <div className="card-header">
                                        <h3>Recent Activity</h3>
                                    </div>
                                    <div className="activity-feed">
                                        {activities.map((act, i) => (
                                            <div key={i} className={`activity-item ${act.type}`}>
                                                <div className="activity-icon">
                                                    <IonIcon icon={act.type === 'critical' ? warningOutline : checkmarkCircleOutline} />
                                                </div>
                                                <div className="activity-content">
                                                    <p>{act.msg}</p>
                                                    <span className="activity-time">{act.time}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="card-footer">
                                        <IonButton fill="clear" color="secondary">
                                            Full Log <IonIcon slot="end" icon={arrowForward} />
                                        </IonButton>
                                    </div>
                                </div>
                            </IonCol>
                        </IonRow>
                    </IonGrid>
                </div>
            </IonContent>
        </IonPage>
    );
};

export default Dashboard;
