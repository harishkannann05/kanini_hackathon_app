import React, { useEffect, useState } from 'react';
import { IonContent, IonPage, IonList, IonItem, IonLabel, IonBadge, IonAvatar, IonButton, IonIcon } from '@ionic/react';
import { peopleOutline } from 'ionicons/icons';
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
                    <h1 className="page-title">
                        <IonIcon icon={peopleOutline} style={{ color: '#4c9aff' }} />
                        Medical Staff On-Duty
                    </h1>

                    {loading ? (
                        <div className="loading-state">Loading doctors...</div>
                    ) : error ? (
                        <div className="loading-state error">{error}</div>
                    ) : doctors.length === 0 ? (
                        <div className="loading-state">No doctors available.</div>
                    ) : (
                        <IonList className="dark-list">
                            {doctors.map(doc => (
                                <IonItem key={doc.doctor_id} className="doctor-item" lines="none">
                                <IonAvatar slot="start">
                                    <div className="doctor-avatar-box">
                                        Dr
                                    </div>
                                </IonAvatar>
                                <IonLabel className="doctor-label">
                                    <h2>Dr. {doc.specialization}</h2>
                                    <p>{doc.department_name}</p>
                                    <p className="exp-badge">{doc.experience_years} Years Experience</p>
                                </IonLabel>
<<<<<<< HEAD
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    {doc._live_activity && (
                                        <IonBadge color="primary">Live</IonBadge>
                                    )}
                                    <IonBadge
                                        slot="end"
                                        className="status-badge"
                                        color={doc.is_available ? 'success' : 'warning'}
                                    >
                                        {doc.is_available ? 'Available' : 'Busy'}
                                    </IonBadge>
                                </div>
                            </IonItem>
                        ))}
                    </IonList>
=======
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        {doc._live_activity && (
                                            <IonBadge color="primary">Live</IonBadge>
                                        )}
                                        <IonBadge
                                            slot="end"
                                            className="status-badge"
                                            color={doc.is_available ? 'success' : 'warning'}
                                        >
                                            {doc.is_available ? 'Available' : 'Busy'}
                                        </IonBadge>
                                    </div>
                                </IonItem>
                            ))}
                        </IonList>
                    )}
>>>>>>> 4803b6e01fb4d333d54e319edc785f55d3b8bfad

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
