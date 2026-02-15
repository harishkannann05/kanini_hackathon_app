import React, { useEffect, useState } from 'react';
import { IonContent, IonPage, IonIcon } from '@ionic/react';
import { statsChartOutline, peopleOutline, gitNetworkOutline } from 'ionicons/icons';
// import { useHistory } from 'react-router-dom';
import api from '../api';
import './AdminDashboard.css';

import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const AdminDashboard: React.FC = () => {
    // const history = useHistory();
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

    const getRiskData = () => {
        if (!stats) return { labels: [], datasets: [] };
        const labels = Object.keys(stats.risk_distribution);
        const data = Object.values(stats.risk_distribution);
        const colors = labels.map(l => l === 'High' ? '#ef4444' : l === 'Medium' ? '#f59e0b' : '#10b981');
        return {
            labels,
            datasets: [{
                data,
                backgroundColor: colors,
                borderColor: '#ffffff',
                borderWidth: 2,
            }]
        };
    };

    const getDeptData = () => {
        if (!stats) return { labels: [], datasets: [] };
        return {
            labels: Object.keys(stats.department_load),
            datasets: [{
                label: 'Active Patients',
                data: Object.values(stats.department_load),
                backgroundColor: '#3b82f6',
                borderRadius: 6,
                barThickness: 20,
            }]
        };
    };

    return (
        <IonPage className="admin-dashboard-page">
            <IonContent className="admin-content">
                <div className="admin-container">

                    {/* Header */}
                    <div className="admin-header animate-enter">
                        <div>
                            <h1>Admin Overview</h1>
                            <p>{new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                        </div>
                    </div>

                    {loading ? (
                        <div className="loading-state">
                            <div className="spinner"></div>
                            <p>Loading Dashboard...</p>
                        </div>
                    ) : stats && (
                        <>
                            {/* Stats Row */}
                            <div className="stats-grid animate-enter" style={{ animationDelay: '0.1s' }}>
                                <div className="stat-card blue">
                                    <div className="stat-icon-wrapper">
                                        <IonIcon icon={peopleOutline} />
                                    </div>
                                    <div className="stat-info">
                                        <h3>Total Visits</h3>
                                        <div className="stat-value">{stats.total_visits}</div>
                                        <div className="stat-trend increasing">
                                            <span>+12%</span> vs last week
                                        </div>
                                    </div>
                                </div>

                                <div className="stat-card purple">
                                    <div className="stat-icon-wrapper">
                                        <IonIcon icon={gitNetworkOutline} />
                                    </div>
                                    <div className="stat-info">
                                        <h3>Active Depts</h3>
                                        <div className="stat-value">{Object.keys(stats.department_load).length}</div>
                                        <div className="stat-sub">Specialties On-Duty</div>
                                    </div>
                                </div>

                                <div className="stat-card orange">
                                    <div className="stat-icon-wrapper">
                                        <IonIcon icon={statsChartOutline} />
                                    </div>
                                    <div className="stat-info">
                                        <h3>High Risk</h3>
                                        <div className="stat-value">{stats.risk_distribution['High'] || 0}</div>
                                        <div className="stat-sub">Critical Cases Today</div>
                                    </div>
                                </div>
                            </div>

                            {/* Charts Section */}
                            <div className="charts-grid animate-enter" style={{ animationDelay: '0.2s' }}>
                                <div className="chart-card">
                                    <div className="chart-header">
                                        <h3>Patient Risk Distribution</h3>
                                    </div>
                                    <div className="chart-body">
                                        <Doughnut
                                            data={getRiskData()}
                                            options={{
                                                maintainAspectRatio: false,
                                                plugins: {
                                                    legend: { position: 'right', labels: { usePointStyle: true, font: { family: 'Inter' } } }
                                                },
                                                cutout: '60%'
                                                /* borderRadius removed from here - not standard for Doughnut options at root, only dataset */
                                            }}
                                        />
                                    </div>
                                </div>

                                <div className="chart-card">
                                    <div className="chart-header">
                                        <h3>Department Load</h3>
                                    </div>
                                    <div className="chart-body">
                                        <Bar
                                            data={getDeptData()}
                                            options={{
                                                maintainAspectRatio: false,
                                                plugins: { legend: { display: false } },
                                                scales: {
                                                    y: {
                                                        beginAtZero: true,
                                                        grid: { color: '#f1f5f9' },
                                                        ticks: { font: { family: 'Inter' } }
                                                    },
                                                    x: {
                                                        grid: { display: false },
                                                        ticks: { font: { family: 'Inter' } }
                                                    }
                                                }
                                            }}
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Recent Activity */}
                            <div className="recent-section animate-enter" style={{ animationDelay: '0.3s' }}>
                                <h3>Recent Activity</h3>
                                <div className="recent-list-card">
                                    {stats.recent_visits.map((v: any, i: number) => (
                                        <div key={v.visit_id} className="recent-item">
                                            <div className="recent-avatar">
                                                {v.patient_name.charAt(0)}
                                            </div>
                                            <div className="recent-info">
                                                <h4>{v.patient_name}</h4>
                                                <span>{v.age}y / {v.gender} • {new Date(v.arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                            </div>
                                            <div className="recent-status">
                                                <span className={`status-badge ${v.status.toLowerCase().replace(' ', '-')}`}>
                                                    {v.status}
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </IonContent>
        </IonPage>
    );
};

export default AdminDashboard;
