import React, { useEffect, useState } from 'react';
import { IonContent, IonPage, IonGrid, IonRow, IonCol, IonButton, IonIcon, IonBadge } from '@ionic/react';
import { peopleOutline, mailOutline, starOutline } from 'ionicons/icons';
import api from '../api';

import { useHistory } from 'react-router-dom';
import './Doctors.css';

const Doctors: React.FC = () => {
    const history = useHistory();
    const [doctors, setDoctors] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        let sockets: Record<string, WebSocket> = {};

        const load = async () => {
            try {
                const res = await api.get('/doctors');
                const docs = res.data || [];
                setDoctors(docs);
                setError('');
                setLoading(false);

                // open websocket for each doctor to receive live queue updates
                docs.forEach((d: any) => {
                    try {
                        const ws = new WebSocket(`ws://127.0.0.1:8000/ws/doctor/${d.doctor_id}`);
                        ws.onopen = () => console.log('ws open', d.doctor_id);
                        ws.onmessage = (evt) => {
                            try {
                                const msg = JSON.parse(evt.data);
                                if (msg.event === 'queue_insert' || msg.event.startsWith('queue_')) {
                                    // indicate there is activity for this doctor
                                    setDoctors(prev => prev.map((p: any) => p.doctor_id === d.doctor_id ? { ...p, _live_activity: true } : p));
                                }
                            } catch (e) { }
                        };
                        ws.onclose = () => { console.log('ws closed', d.doctor_id); };
                        sockets[d.doctor_id] = ws;
                    } catch (err) {
                        console.warn('WS failed for', d.doctor_id, err);
                    }
                });
            } catch (err) {
                console.error(err);
                setError('Failed to load doctors.');
                setLoading(false);
            }
        };

        load();

        return () => {
            Object.values(sockets).forEach(s => { try { s.close(); } catch (e) { } });
        };
    }, []);

    return (
        <IonPage className="doctors-page">
            <IonContent className="dark-content">
                <div className="doctors-container">
                    <div className="doctors-header animate-enter">
                        <h1 className="page-title">
                            <IonIcon icon={peopleOutline} />
                            Medical Staff On-Duty
                        </h1>
                        <p className="page-subtitle">Real-time availability and status</p>
                    </div>

                    {loading ? (
                        <div className="loading-state">Loading doctors...</div>
                    ) : error ? (
                        <div className="loading-state error">{error}</div>
                    ) : doctors.length === 0 ? (
                        <div className="loading-state">No doctors available.</div>
                    ) : (
                        <IonGrid style={{ padding: 0 }}>
                            <IonRow>
                                {doctors.map((doc, idx) => (
                                    <IonCol size="12" sizeMd="6" sizeLg="4" key={doc.doctor_id} className="animate-card" style={{ animationDelay: `${idx * 0.1}s` }}>
                                        <div className="doctor-card-premium">
                                            <div className="doc-card-header">
                                                <div className="doc-avatar">
                                                    {doc.full_name ? doc.full_name.replace(/^(Dr\.|Dr)\s*/i, '').charAt(0) : 'D'}
                                                </div>
                                                <div className="doc-info">
                                                    <h3>{doc.full_name}</h3>
                                                    <span className="doc-dept">{doc.department_name}</span>
                                                </div>
                                                <div className={`doc-status-dot ${doc.is_available ? 'available' : 'busy'}`}></div>
                                            </div>

                                            <div className="doc-card-body">
                                                <div className="doc-meta-row">
                                                    <IonIcon icon={mailOutline} />
                                                    <span>{doc.email}</span>
                                                </div>
                                                <div className="doc-meta-row">
                                                    <IonIcon icon={starOutline} />
                                                    <span>{doc.experience_years} Years Experience</span>
                                                </div>
                                            </div>

                                            <div className="doc-card-footer">
                                                <span className={`status-text ${doc.is_available ? 'available' : 'busy'}`}>
                                                    {doc.is_available ? 'Available Now' : 'Currently Busy'}
                                                </span>
                                                {doc._live_activity && (
                                                    <div className="live-indicator">
                                                        <div className="pulsing-dot-small"></div> Active
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </IonCol>
                                ))}
                            </IonRow>
                        </IonGrid>
                    )}

                    <div className="back-container">
                        <IonButton
                            fill="clear"
                            className="back-btn"
                            onClick={() => history.push('/dashboard')}
                        >
                            Return to Dashboard
                        </IonButton>
                    </div>
                </div>
            </IonContent>
        </IonPage>
    );
};

export default Doctors;

