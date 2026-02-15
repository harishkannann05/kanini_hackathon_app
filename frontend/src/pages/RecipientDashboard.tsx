import React, { useState, useEffect } from 'react';
import {
    IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonButton,
    IonSegment, IonSegmentButton, IonLabel, IonItem, IonInput, IonList,
    IonCard, IonCardContent, IonSearchbar, IonGrid, IonRow, IonCol,
    IonIcon, IonModal, IonTextarea, IonSelect, IonSelectOption, IonToast,
    IonListHeader, IonNote, IonToggle
} from '@ionic/react';
import { searchOutline, personAddOutline, personOutline, phonePortraitOutline } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import api from '../api';
import './RecipientDashboard.css';

const RecipientDashboard: React.FC = () => {
    const history = useHistory();
    const [segment, setSegment] = useState<'search' | 'register'>('search');
    const [searchText, setSearchText] = useState('');
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [showTriageModal, setShowTriageModal] = useState(false);
    const [selectedPatient, setSelectedPatient] = useState<any>(null);
    const [toastMsg, setToastMsg] = useState('');
    const [showToast, setShowToast] = useState(false);
    const [usePreferredDoctor, setUsePreferredDoctor] = useState(true);

    // Symptom Autocomplete
    const [symptomInput, setSymptomInput] = useState('');
    const [symptomSuggestions, setSymptomSuggestions] = useState<any[]>([]);

    useEffect(() => {
        if (segment === 'search') {
            loadInitialPatients();
        }
    }, [segment]);

    const loadInitialPatients = async () => {
        try {
            const res = await api.get('/recipient/patients/search?q=');
            setSearchResults(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    // Register Form
    const [regForm, setRegForm] = useState({
        full_name: '', age: '', gender: 'Male' as string, phone_number: '',
        symptoms: '', blood_pressure: '120/80', heart_rate: '72', temperature: '37.0',
        pre_existing_conditions: ''
    });

    // Triage Form
    const [triageForm, setTriageForm] = useState({
        symptoms: '', systolic_bp: 120, heart_rate: 72, temperature: 37.0,
        chronic_conditions: '', visit_type: 'Walk-In'
    });

    const handleSearch = async (val: string) => {
        setSearchText(val);
        try {
            const res = await api.get(`/recipient/patients/search?q=${val}`);
            setSearchResults(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleSymptomSearch = async (val: string) => {
        setSymptomInput(val);
        if (val.length < 2) {
            setSymptomSuggestions([]);
            return;
        }
        try {
            const res = await api.get(`/master/symptoms?q=${val}`);
            setSymptomSuggestions(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const addSymptom = (sName: string, isFromReg: boolean) => {
        if (isFromReg) {
            const current = regForm.symptoms ? regForm.symptoms.split(',').map(s => s.trim()) : [];
            if (!current.includes(sName)) {
                setRegForm({ ...regForm, symptoms: [...current, sName].join(', ') });
            }
        } else {
            const current = triageForm.symptoms ? triageForm.symptoms.split(',').map(s => s.trim()) : [];
            if (!current.includes(sName)) {
                setTriageForm({ ...triageForm, symptoms: [...current, sName].join(', ') });
            }
        }
        setSymptomInput('');
        setSymptomSuggestions([]);
    };

    const handleRegister = async () => {
        if (!regForm.full_name.trim()) {
            setToastMsg('Full name is required.');
            setShowToast(true);
            return;
        }
        if (!regForm.phone_number.trim()) {
            setToastMsg('Phone number is required.');
            setShowToast(true);
            return;
        }
        if (!regForm.age) {
            setToastMsg('Age is required.');
            setShowToast(true);
            return;
        }
        if (!regForm.symptoms.trim()) {
            setToastMsg('Please add at least one symptom.');
            setShowToast(true);
            return;
        }

        try {
            const payload = {
                ...regForm,
                age: parseInt(regForm.age),
                heart_rate: parseInt(regForm.heart_rate),
                temperature: parseFloat(regForm.temperature)
            };
            const res = await api.post('/recipient/patients', payload);
            setToastMsg("Patient Registered!");
            setShowToast(true);
            setSelectedPatient(res.data);
            setTriageForm({
                ...triageForm,
                symptoms: regForm.symptoms,
                systolic_bp: parseInt(regForm.blood_pressure.split('/')[0]) || 120,
                heart_rate: parseInt(regForm.heart_rate),
                temperature: parseFloat(regForm.temperature)
            });
            setShowTriageModal(true);
        } catch (err) {
            console.error(err);
            const detail = (err as any).response?.data?.detail;
            if (typeof detail === 'string') {
                setToastMsg(detail);
            } else if (Array.isArray(detail)) {
                setToastMsg(detail.map((e: any) => `${e.loc[1]}: ${e.msg}`).join('\n'));
            } else {
                setToastMsg('Registration Failed');
            }
            setShowToast(true);
        }
    };

    const handleTriageSubmit = async () => {
        if (!selectedPatient) return;
        if (!triageForm.symptoms.trim()) {
            setToastMsg('Please add at least one symptom.');
            setShowToast(true);
            return;
        }
        try {
            const payload = {
                patient_id: selectedPatient.patient_id,
                age: selectedPatient.age,
                gender: selectedPatient.gender,
                systolic_bp: triageForm.systolic_bp,
                heart_rate: triageForm.heart_rate,
                temperature: triageForm.temperature,
                symptoms: triageForm.symptoms.split(',').map(s => s.trim()).filter(s => s),
                chronic_conditions: triageForm.chronic_conditions.split(',').map(s => s.trim()).filter(s => s),
                visit_type: triageForm.visit_type,
                use_preferred_doctor: usePreferredDoctor
            };

            const res = await api.post('/visits', payload);
            setToastMsg(`Visit Created! Risk: ${res.data.risk_level}`);
            setShowToast(true);
            setShowTriageModal(false);
            setSegment('search');
            setSearchText('');
        } catch (err) {
            console.error(err);
            const detail = (err as any).response?.data?.detail;
            if (typeof detail === 'string') {
                setToastMsg(detail);
            } else if (Array.isArray(detail)) {
                setToastMsg(detail.map((e: any) => `${e.loc[1]}: ${e.msg}`).join('\n'));
            } else {
                setToastMsg('Triage Failed');
            }
            setShowToast(true);
        }
    };

    const openTriage = (patient: any) => {
        setSelectedPatient(patient);
        setTriageForm({
            ...triageForm,
            symptoms: '',
            chronic_conditions: ''
        });
        setUsePreferredDoctor(true);
        setShowTriageModal(true);
    };

    return (
        <IonPage className="recipient-page">
            <IonHeader>
                <IonToolbar color="tertiary">
                    <IonTitle>Triage Officer Dashboard</IonTitle>
                    <IonButtons slot="end">
                        <IonButton onClick={() => {
                            localStorage.clear();
                            history.replace('/login');
                        }}>Logout</IonButton>
                    </IonButtons>
                </IonToolbar>
            </IonHeader>

            <IonContent className="ion-padding">
                <IonSegment value={segment} onIonChange={(e: any) => setSegment(e.detail.value as any)} className="role-segment">
                    <IonSegmentButton value="search">
                        <IonLabel>Search Patient</IonLabel>
                        <IonIcon icon={searchOutline} />
                    </IonSegmentButton>
                    <IonSegmentButton value="register">
                        <IonLabel>New Patient</IonLabel>
                        <IonIcon icon={personAddOutline} />
                    </IonSegmentButton>
                </IonSegment>

                {segment === 'search' && (
                    <div className="search-section">
                        <IonSearchbar
                            value={searchText}
                            onIonInput={(e: any) => handleSearch(e.detail.value!)}
                            debounce={300}
                            placeholder="Search by Name or Phone"
                            className="custom-search"
                        />

                        <IonList lines="full" className="engine-search-results">
                            <IonListHeader>
                                <IonLabel>Results ({searchResults.length})</IonLabel>
                            </IonListHeader>
                            {searchResults.length === 0 && <IonItem><IonLabel>No patients found</IonLabel></IonItem>}
                            {searchResults.map(p => (
                                <IonItem key={p.patient_id} button onClick={() => openTriage(p)} detail={true}>
                                    <IonIcon icon={personOutline} slot="start" color="primary" />
                                    <IonLabel>
                                        <h2 style={{ fontWeight: 'bold' }}>{p.full_name}</h2>
                                        <p style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                                            <IonIcon icon={phonePortraitOutline} /> {p.phone_number} | {p.gender}, {p.age}y
                                        </p>
                                        {p.risk_level && <IonNote color={p.risk_level === 'High' ? 'danger' : 'medium'}>Last Risk: {p.risk_level}</IonNote>}
                                    </IonLabel>
                                </IonItem>
                            ))}
                        </IonList>
                    </div>
                )}

                {segment === 'register' && (
                    <div className="register-form">
                        <IonCard className="form-card">
                            <IonCardContent>
                                <form>
                                    <IonItem><IonLabel position="stacked">Full Name</IonLabel><IonInput value={regForm.full_name} onIonChange={(e: any) => setRegForm({ ...regForm, full_name: e.detail.value! })} placeholder="Enter full name" /></IonItem>
                                    <IonItem><IonLabel position="stacked">Phone</IonLabel><IonInput value={regForm.phone_number} onIonChange={(e: any) => setRegForm({ ...regForm, phone_number: e.detail.value! })} placeholder="91-XXXXXXXXXX" /></IonItem>
                                    <IonGrid><IonRow>
                                        <IonCol><IonItem><IonLabel position="stacked">Age</IonLabel><IonInput type="number" value={regForm.age} onIonChange={(e: any) => setRegForm({ ...regForm, age: e.detail.value! })} /></IonItem></IonCol>
                                        <IonCol><IonItem><IonLabel position="stacked">Gender</IonLabel><IonSelect value={regForm.gender} onIonChange={(e: any) => setRegForm({ ...regForm, gender: e.detail.value })}><IonSelectOption value="Male">Male</IonSelectOption><IonSelectOption value="Female">Female</IonSelectOption></IonSelect></IonItem></IonCol>
                                    </IonRow></IonGrid>

                                    <IonItem>
                                        <IonLabel position="stacked">Symptoms</IonLabel>
                                        <IonInput value={symptomInput} onIonInput={(e: any) => handleSymptomSearch(e.detail.value!)} placeholder="Type symptom to search..." />
                                    </IonItem>
                                    {symptomSuggestions.length > 0 && (
                                        <IonList className="autocomplete-list">
                                            {symptomSuggestions.map((s, idx) => (
                                                <IonItem key={idx} button onClick={() => addSymptom(s.name, true)} color="light">
                                                    <IonLabel>{s.name}</IonLabel>
                                                </IonItem>
                                            ))}
                                        </IonList>
                                    )}
                                    <IonTextarea value={regForm.symptoms} onIonChange={(e: any) => setRegForm({ ...regForm, symptoms: e.detail.value! })} placeholder="Selected symptoms appear here..." rows={3} disabled />

                                    <IonButton expand="block" shape="round" className="ion-margin-top" onClick={handleRegister}>Register & Triage</IonButton>
                                </form>
                            </IonCardContent>
                        </IonCard>
                    </div>
                )}

                <IonModal className="triage-modal" isOpen={showTriageModal} onDidDismiss={() => setShowTriageModal(false)}>
                    <IonHeader>
                        <IonToolbar color="primary">
                            <IonTitle>Triage Check-In</IonTitle>
                            <IonButtons slot="end"><IonButton onClick={() => setShowTriageModal(false)}>Close</IonButton></IonButtons>
                        </IonToolbar>
                    </IonHeader>
                    <IonContent className="ion-padding">
                        {selectedPatient && (
                            <IonCard className="patient-card-header">
                                <IonCardContent>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                                        <div className="avatar-placeholder">{selectedPatient.full_name.charAt(0)}</div>
                                        <div>
                                            <h2 style={{ margin: 0 }}>{selectedPatient.full_name}</h2>
                                            <p style={{ margin: 0 }}>{selectedPatient.gender}, {selectedPatient.age} years | {selectedPatient.phone_number}</p>
                                        </div>
                                    </div>
                                </IonCardContent>
                            </IonCard>
                        )}
                        <IonList>
                            <IonItem>
                                <IonLabel position="stacked">Search Symptoms</IonLabel>
                                <IonInput value={symptomInput} onIonInput={(e: any) => handleSymptomSearch(e.detail.value!)} placeholder="Typing 'Fever'..." />
                            </IonItem>
                            {symptomSuggestions.length > 0 && (
                                <IonList className="autocomplete-list">
                                    {symptomSuggestions.map((s, idx) => (
                                        <IonItem key={idx} button onClick={() => addSymptom(s.name, false)} color="light">
                                            <IonLabel>{s.name}</IonLabel>
                                        </IonItem>
                                    ))}
                                </IonList>
                            )}
                            <IonItem><IonLabel position="stacked">Selected Symptoms (Comma separated)</IonLabel><IonTextarea value={triageForm.symptoms} onIonChange={(e: any) => setTriageForm({ ...triageForm, symptoms: e.detail.value! })} rows={2} /></IonItem>

                            <IonItem><IonLabel position="stacked">Chronic Conditions</IonLabel><IonTextarea value={triageForm.chronic_conditions} onIonChange={(e: any) => setTriageForm({ ...triageForm, chronic_conditions: e.detail.value! })} /></IonItem>
                            <IonGrid>
                                <IonRow>
                                    <IonCol><IonItem><IonLabel position="stacked">Systolic BP</IonLabel><IonInput type="number" value={triageForm.systolic_bp} onIonChange={(e: any) => setTriageForm({ ...triageForm, systolic_bp: parseInt(e.detail.value!, 10) })} /></IonItem></IonCol>
                                    <IonCol><IonItem><IonLabel position="stacked">Heart Rate</IonLabel><IonInput type="number" value={triageForm.heart_rate} onIonChange={(e: any) => setTriageForm({ ...triageForm, heart_rate: parseInt(e.detail.value!, 10) })} /></IonItem></IonCol>
                                    <IonCol><IonItem><IonLabel position="stacked">Temp (°C)</IonLabel><IonInput type="number" value={triageForm.temperature} onIonChange={(e: any) => setTriageForm({ ...triageForm, temperature: parseFloat(e.detail.value!) })} /></IonItem></IonCol>
                                </IonRow>
                            </IonGrid>
                            <IonItem>
                                <IonLabel>Visit Type</IonLabel>
                                <IonSelect value={triageForm.visit_type} onIonChange={(e: any) => setTriageForm({ ...triageForm, visit_type: e.detail.value })}>
                                    <IonSelectOption value="Walk-In">Walk-In</IonSelectOption>
                                    <IonSelectOption value="Emergency">Emergency</IonSelectOption>
                                    <IonSelectOption value="Follow-up">Follow-up</IonSelectOption>
                                </IonSelect>
                            </IonItem>
                            <IonItem>
                                <IonLabel>Prefer previous doctor</IonLabel>
                                <IonToggle checked={usePreferredDoctor} onIonChange={(e: any) => setUsePreferredDoctor(e.detail.checked)} />
                            </IonItem>
                        </IonList>
                        <IonButton expand="block" shape="round" className="ion-margin-top" color="success" onClick={handleTriageSubmit}>Submit & Assign Doctor</IonButton>
                    </IonContent>
                </IonModal>

                <IonToast isOpen={showToast} onDidDismiss={() => setShowToast(false)} message={toastMsg} duration={2000} color="dark" />
            </IonContent>
        </IonPage>
    );
};

export default RecipientDashboard;
