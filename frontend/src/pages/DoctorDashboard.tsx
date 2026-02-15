import React, { useEffect, useState, useRef } from 'react';
import {
    IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonButton,
    IonCard, IonCardContent, IonBadge, IonList, IonItem, IonLabel, IonNote,
    IonChip, IonIcon, IonToast, IonGrid, IonRow, IonCol, IonModal, IonCardHeader, IonCardTitle,
    IonInput, IonTextarea, IonToggle
} from '@ionic/react';
import { useHistory } from 'react-router-dom';
import { playOutline, checkmarkDoneOutline, pulseOutline, timeOutline, personOutline, medkitOutline } from 'ionicons/icons';
import api from '../api';
import './DoctorDashboard.css';

interface QueueItem {
    queue_id: string;
    visit_id: string;
    patient_name: string;
    patient_id?: string;
    age: number;
    gender: string;
    symptoms: string;
    risk_level: string;
    priority_score: number;
    dynamic_score: number;
    queue_position: number;
    is_emergency: boolean;
    waiting_minutes: number;
    wait_time_boost?: number;
    position: number;
    visit_status?: string;
}

interface PatientInsight {
    chronic_conditions: Array<{ condition: string; confidence: number; source: string }>;
    recent_high_risk: Array<{ finding: string; date: string; confidence: number }>;
    medications: Array<{ name: string; dosage: string; prescribed_date: string }>;
    recurring_symptoms: Record<string, number>;
    summary: string;
}

const DoctorDashboard: React.FC = () => {
    const history = useHistory();
    const [queue, setQueue] = useState<QueueItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [wsConnected, setWsConnected] = useState(false);
    const [showInsightsModal, setShowInsightsModal] = useState(false);
    const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
    const [patientInsights, setPatientInsights] = useState<PatientInsight | null>(null);
    const [insightsLoading, setInsightsLoading] = useState(false);
    const [showRecordModal, setShowRecordModal] = useState(false);
    const [selectedVisitId, setSelectedVisitId] = useState<string | null>(null);
    const [toastMessage, setToastMessage] = useState('');
    const [showToast, setShowToast] = useState(false);
    const [recordForm, setRecordForm] = useState({
        diagnosis: '',
        syndrome_identified: '',
        treatment_plan: '',
        follow_up_required: false,
        follow_up_date: '',
        notes: ''
    });
    const maxRetries = 5;
    const retryCount = useRef(0);
    const doctorId = localStorage.getItem('doctor_id');

    useEffect(() => {
        if (!doctorId) {
            history.replace('/login');
            return;
        }
        fetchQueue();
        connectWebSocket();

        // Polling fallback every 30s
        const interval = setInterval(fetchQueue, 30000);
        return () => {
            clearInterval(interval);
            if (ws.current) ws.current.close();
        };
    }, [doctorId]);

    const fetchQueue = async () => {
        try {
            const res = await api.get(`/doctor/queue/${doctorId}`);
            setQueue(res.data.queue);
            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch queue", err);
            setToastMessage('Failed to load queue.');
            setShowToast(true);
        }
    };

    const ws = useRef<WebSocket | null>(null);

    const connectWebSocket = () => {
        if (!doctorId) return;
        const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        // Assuming backend is on port 8000, different from frontend port
        // We use absolute URL for WS
        const wsUrl = `ws://127.0.0.1:8000/ws/doctor/${doctorId}`;

        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            console.log("WS Connected");
            setWsConnected(true);
            retryCount.current = 0;
        };

        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.event === 'connected') return;

            // On any queue update, re-fetch the full queue to ensure consistency
            // (Simpler than merging updates manually)
            if (data.queue && Array.isArray(data.queue)) {
                setQueue(data.queue);
                return;
            }

            if (data.event.startsWith('queue_') || data.event === 'queue_insert') {
                fetchQueue();
            }
        };

        ws.current.onclose = () => {
            setWsConnected(false);
            if (retryCount.current < maxRetries) {
                setTimeout(connectWebSocket, 3000);
                retryCount.current++;
            }
        };
    };

    const handleAction = async (queueId: string, action: 'start' | 'complete') => {
        try {
            await api.post(`/doctor/queue/${queueId}/serve`, { action });
            fetchQueue(); // Optimistic update or wait for WS
        } catch (err) {
            console.error(`Failed to ${action}`, err);
            setToastMessage(`Failed to ${action} consultation.`);
            setShowToast(true);
        }
    };

    const getRiskColor = (level: string) => {
        switch (level) {
            case 'High': return 'danger';
            case 'Medium': return 'warning';
            default: return 'success';
        }
    };

    const getWaitTimeColor = (minutes: number) => {
        if (minutes > 60) return 'danger'; // Red for >60 min
        if (minutes > 30) return 'warning'; // Yellow for >30 min
        return 'success'; // Green for <=30 min
    };

    const fetchPatientInsights = async (patientId: string) => {
        setInsightsLoading(true);
        try {
            const res = await api.get(`/patient/${patientId}/insights`);
            setPatientInsights(res.data);
            setShowInsightsModal(true);
        } catch (err) {
            console.error('Failed to fetch insights', err);
            setToastMessage('Failed to load patient insights.');
            setShowToast(true);
        } finally {
            setInsightsLoading(false);
        }
    };

    const openRecordModal = (visitId: string) => {
        setSelectedVisitId(visitId);
        setRecordForm({
            diagnosis: '',
            syndrome_identified: '',
            treatment_plan: '',
            follow_up_required: false,
            follow_up_date: '',
            notes: ''
        });
        setShowRecordModal(true);
    };

    const submitRecord = async () => {
        if (!selectedVisitId || !doctorId) return;
        try {
            await api.post(`/doctor/visits/${selectedVisitId}/record`, {
                ...recordForm,
                doctor_id: doctorId
            });
            setShowRecordModal(false);
        } catch (err) {
            console.error('Failed to submit record', err);
            setToastMessage('Failed to submit report.');
            setShowToast(true);
        }
    };

    return (
        <IonPage className="doctor-page">


            <IonContent className="ion-padding doctor-content">
                <div className="dashboard-header animate-enter" style={{ animationDelay: '0s' }}>
                    <div className="header-greeting">
                        <h1>Hello, Doctor.</h1>
                        <p>{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                    </div>
                    <div className={`status-indicator ${wsConnected ? 'online' : 'offline'}`} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'white', padding: '8px 16px', borderRadius: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', fontSize: '0.9rem', fontWeight: '600', color: wsConnected ? '#10b981' : '#ef4444' }}>
                        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: wsConnected ? '#10b981' : '#ef4444' }}></div>
                        {wsConnected ? 'Live Updates' : 'Reconnecting...'}
                    </div>
                </div>

                {/* Metrics Grid */}
                <IonGrid style={{ padding: 0 }}>
                    <IonRow>
                        <IonCol size="12" sizeMd="4" className="animate-enter" style={{ animationDelay: '0.1s' }}>
                            <div className="doctor-stat-card blue">
                                <div className="stat-icon-wrapper"><IonIcon icon={personOutline} /></div>
                                <div className="stat-info">
                                    <h3>{queue.length}</h3>
                                    <p>Patients Waiting</p>
                                </div>
                            </div>
                        </IonCol>
                        <IonCol size="12" sizeMd="4" className="animate-enter" style={{ animationDelay: '0.15s' }}>
                            <div className="doctor-stat-card orange">
                                <div className="stat-icon-wrapper"><IonIcon icon={pulseOutline} /></div>
                                <div className="stat-info">
                                    <h3>{queue.filter(p => p.risk_level === 'High' || p.is_emergency).length}</h3>
                                    <p>Critical Cases</p>
                                </div>
                            </div>
                        </IonCol>
                        <IonCol size="12" sizeMd="4" className="animate-enter" style={{ animationDelay: '0.2s' }}>
                            <div className="doctor-stat-card teal">
                                <div className="stat-icon-wrapper"><IonIcon icon={timeOutline} /></div>
                                <div className="stat-info">
                                    <h3>{queue.length > 0 ? Math.round(queue.reduce((acc, curr) => acc + curr.waiting_minutes, 0) / queue.length) : 0}m</h3>
                                    <p>Avg. Wait Time</p>
                                </div>
                            </div>
                        </IonCol>
                    </IonRow>
                </IonGrid>

                <div className="queue-section-header animate-enter" style={{ animationDelay: '0.25s' }}>
                    <h2>Patient Queue</h2>
                    <span className="queue-subtext">Sorted by AI Priority & Wait Time</span>
                </div>

                {loading ? (
                    <div className="loading-state" style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>Loading Queue...</div>
                ) : queue.length === 0 ? (
                    <div className="empty-state animate-enter" style={{ animationDelay: '0.3s', textAlign: 'center', padding: '4rem', background: 'white', borderRadius: '24px', boxShadow: '0 10px 30px rgba(0,0,0,0.03)' }}>
                        <IonIcon icon={checkmarkDoneOutline} style={{ fontSize: '4rem', color: '#cbd5e1', marginBottom: '1rem' }} />
                        <h3 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#475569', marginBottom: '0.5rem' }}>All Caught Up!</h3>
                        <p style={{ color: '#94a3b8' }}>No patients in queue. Enjoy your break! ☕</p>
                    </div>
                ) : (
                    <div className="queue-container">
                        {/* Active Patient (Hero) */}
                        {queue.length > 0 && (() => {
                            const active = queue[0];
                            return (
                                <div className="active-patient-card animate-enter" style={{ animationDelay: '0.3s' }}>
                                    <div className="active-badge">
                                        <div className="pulsing-dot"></div> Now Serving
                                    </div>
                                    <div className="active-patient-header">
                                        <div className="patient-avatar-large">
                                            {active.patient_name.charAt(0)}
                                        </div>
                                        <div className="active-patient-info">
                                            <h3>{active.patient_name}</h3>
                                            <div className="patient-meta">
                                                <span><IonIcon icon={personOutline} /> {active.age}y / {active.gender}</span>
                                                <span className={`queue-risk-badge ${active.risk_level}`} style={{ fontSize: '0.9rem' }}>{active.risk_level} Risk</span>
                                                <span><IonIcon icon={timeOutline} /> {active.waiting_minutes}m wait</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="active-symptoms">
                                        <span className="symptom-label">Reported Symptoms</span>
                                        <p className="symptom-text">"{active.symptoms}"</p>
                                        <div style={{ marginTop: '1rem', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                                            {active.patient_id && (
                                                <IonChip onClick={() => fetchPatientInsights(active.patient_id!)} color="primary" mode="ios" outline style={{ margin: 0 }}>
                                                    <IonIcon icon={medkitOutline} /> Medical Insights
                                                </IonChip>
                                            )}
                                            <IonChip color="secondary" mode="ios" outline style={{ margin: 0 }}>
                                                Triage Score: {active.priority_score}
                                            </IonChip>
                                            {active.is_emergency && <IonBadge color="danger" style={{ padding: '8px 12px', borderRadius: '12px' }}>EMERGENCY</IonBadge>}
                                        </div>
                                    </div>

                                    <div className="active-actions">
                                        <IonButton
                                            className="action-btn" size="default" color="success"
                                            onClick={() => handleAction(active.queue_id, 'start')}
                                            disabled={active.visit_status === 'In Consultation'}
                                            style={{ flex: 1 }}
                                        >
                                            <IonIcon icon={playOutline} slot="start" /> Start Visit
                                        </IonButton>
                                        <IonButton
                                            className="action-btn" size="default" color="tertiary"
                                            onClick={() => openRecordModal(active.visit_id)}
                                            style={{ flex: 1 }}
                                        >
                                            Add Medical Report
                                        </IonButton>
                                        <IonButton
                                            className="action-btn" size="default" color="medium" fill="outline"
                                            onClick={() => handleAction(active.queue_id, 'complete')}
                                            style={{ flex: 1 }}
                                        >
                                            <IonIcon icon={checkmarkDoneOutline} slot="start" /> Complete
                                        </IonButton>
                                    </div>
                                </div>
                            );
                        })()}

                        {/* Upcoming List */}
                        {queue.length > 1 && (
                            <div className="upcoming-list animate-enter" style={{ animationDelay: '0.4s' }}>
                                <h3 style={{ fontSize: '1.1rem', color: '#64748b', margin: '2rem 0 1rem 0', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Up Next ({queue.length - 1})</h3>
                                {queue.slice(1).map((item, idx) => (
                                    <div key={item.queue_id} className="queue-card-item">
                                        <div className="queue-pos-badge">#{item.position}</div>
                                        <div className="queue-card-info">
                                            <h4>{item.patient_name}</h4>
                                            <div className="queue-card-meta">
                                                <span>{item.age}y / {item.gender}</span>
                                                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><IonIcon icon={timeOutline} style={{ fontSize: '0.9rem' }} /> {item.waiting_minutes}m</span>
                                            </div>
                                        </div>
                                        <div className="queue-card-status">
                                            <span className={`queue-risk-badge ${item.risk_level}`}>{item.risk_level}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </IonContent>

            {/* Patient Insights Modal */}
            <IonModal isOpen={showInsightsModal} onDidDismiss={() => setShowInsightsModal(false)}>
                <IonHeader>
                    <IonToolbar>
                        <IonTitle>Patient Medical Insights</IonTitle>
                        <IonButtons slot="end">
                            <IonButton onClick={() => setShowInsightsModal(false)}>Close</IonButton>
                        </IonButtons>
                    </IonToolbar>
                </IonHeader>
                <IonContent className="ion-padding">
                    {patientInsights && (
                        <div className="insights-container">
                            {/* Summary */}
                            <IonCard>
                                <IonCardHeader>
                                    <IonCardTitle>Summary</IonCardTitle>
                                </IonCardHeader>
                                <IonCardContent>
                                    <p>{patientInsights.summary}</p>
                                </IonCardContent>
                            </IonCard>

                            {/* Chronic Conditions */}
                            {patientInsights.chronic_conditions.length > 0 && (
                                <IonCard>
                                    <IonCardHeader>
                                        <IonCardTitle>🔴 Chronic Conditions</IonCardTitle>
                                    </IonCardHeader>
                                    <IonCardContent>
                                        <IonList>
                                            {patientInsights.chronic_conditions.map((cond, idx) => (
                                                <IonItem key={idx}>
                                                    <IonLabel>
                                                        <h3>{cond.condition}</h3>
                                                        <p>Source: {cond.source} (Confidence: {(cond.confidence * 100).toFixed(0)}%)</p>
                                                    </IonLabel>
                                                </IonItem>
                                            ))}
                                        </IonList>
                                    </IonCardContent>
                                </IonCard>
                            )}

                            {/* Recent High-Risk Findings */}
                            {patientInsights.recent_high_risk.length > 0 && (
                                <IonCard>
                                    <IonCardHeader>
                                        <IonCardTitle>⚠️ Recent High-Risk Findings</IonCardTitle>
                                    </IonCardHeader>
                                    <IonCardContent>
                                        <IonList>
                                            {patientInsights.recent_high_risk.map((finding, idx) => (
                                                <IonItem key={idx}>
                                                    <IonLabel>
                                                        <h3>{finding.finding}</h3>
                                                        <p>Date: {finding.date}</p>
                                                    </IonLabel>
                                                    <IonBadge slot="end" color="warning">
                                                        {(finding.confidence * 100).toFixed(0)}%
                                                    </IonBadge>
                                                </IonItem>
                                            ))}
                                        </IonList>
                                    </IonCardContent>
                                </IonCard>
                            )}

                            {/* Medications */}
                            {patientInsights.medications.length > 0 && (
                                <IonCard>
                                    <IonCardHeader>
                                        <IonCardTitle>💊 Current Medications</IonCardTitle>
                                    </IonCardHeader>
                                    <IonCardContent>
                                        <IonList>
                                            {patientInsights.medications.map((med, idx) => (
                                                <IonItem key={idx}>
                                                    <IonLabel>
                                                        <h3>{med.name}</h3>
                                                        <p>Dosage: {med.dosage} | Prescribed: {med.prescribed_date}</p>
                                                    </IonLabel>
                                                </IonItem>
                                            ))}
                                        </IonList>
                                    </IonCardContent>
                                </IonCard>
                            )}

                            {/* Recurring Symptoms */}
                            {Object.keys(patientInsights.recurring_symptoms).length > 0 && (
                                <IonCard>
                                    <IonCardHeader>
                                        <IonCardTitle>🔄 Recurring Symptoms</IonCardTitle>
                                    </IonCardHeader>
                                    <IonCardContent>
                                        <IonList>
                                            {Object.entries(patientInsights.recurring_symptoms).map(([symptom, count]) => (
                                                <IonItem key={symptom}>
                                                    <IonLabel>{symptom}</IonLabel>
                                                    <IonBadge slot="end" color="primary">{count} occurrences</IonBadge>
                                                </IonItem>
                                            ))}
                                        </IonList>
                                    </IonCardContent>
                                </IonCard>
                            )}
                        </div>
                    )}
                </IonContent>
            </IonModal>

            {/* Medical Record Modal */}
            <IonModal isOpen={showRecordModal} onDidDismiss={() => setShowRecordModal(false)}>
                <IonHeader>
                    <IonToolbar>
                        <IonTitle>Consultation Report</IonTitle>
                        <IonButtons slot="end">
                            <IonButton onClick={() => setShowRecordModal(false)}>Close</IonButton>
                        </IonButtons>
                    </IonToolbar>
                </IonHeader>
                <IonContent className="ion-padding">
                    <IonItem>
                        <IonLabel position="stacked">Diagnosis</IonLabel>
                        <IonInput
                            value={recordForm.diagnosis}
                            onIonChange={(e) => setRecordForm({ ...recordForm, diagnosis: e.detail.value || '' })}
                        />
                    </IonItem>
                    <IonItem>
                        <IonLabel position="stacked">Syndrome Identified</IonLabel>
                        <IonInput
                            value={recordForm.syndrome_identified}
                            onIonChange={(e) => setRecordForm({ ...recordForm, syndrome_identified: e.detail.value || '' })}
                        />
                    </IonItem>
                    <IonItem>
                        <IonLabel position="stacked">Treatment Plan</IonLabel>
                        <IonTextarea
                            value={recordForm.treatment_plan}
                            onIonChange={(e) => setRecordForm({ ...recordForm, treatment_plan: e.detail.value || '' })}
                            rows={3}
                        />
                    </IonItem>
                    <IonItem>
                        <IonLabel>Follow-up Required</IonLabel>
                        <IonToggle
                            checked={recordForm.follow_up_required}
                            onIonChange={(e) => setRecordForm({ ...recordForm, follow_up_required: e.detail.checked })}
                        />
                    </IonItem>
                    <IonItem>
                        <IonLabel position="stacked">Follow-up Date (YYYY-MM-DD)</IonLabel>
                        <IonInput
                            value={recordForm.follow_up_date}
                            onIonChange={(e) => setRecordForm({ ...recordForm, follow_up_date: e.detail.value || '' })}
                        />
                    </IonItem>
                    <IonItem>
                        <IonLabel position="stacked">Notes</IonLabel>
                        <IonTextarea
                            value={recordForm.notes}
                            onIonChange={(e) => setRecordForm({ ...recordForm, notes: e.detail.value || '' })}
                            rows={4}
                        />
                    </IonItem>
                    <IonButton expand="block" className="ion-margin-top" onClick={submitRecord}>
                        Save Report
                    </IonButton>
                </IonContent>
            </IonModal>
            <IonToast
                isOpen={showToast}
                onDidDismiss={() => setShowToast(false)}
                message={toastMessage}
                duration={2500}
                color="danger"
            />
        </IonPage>
    );
};

export default DoctorDashboard;
