import React, { useState, useEffect } from 'react';
import {
    IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonButton,
    IonSegment, IonSegmentButton, IonLabel, IonItem, IonInput, IonList,
    IonCard, IonCardContent, IonSearchbar, IonGrid, IonRow, IonCol,
    IonIcon, IonModal, IonTextarea, IonSelect, IonSelectOption, IonToast,
    IonNote, IonToggle
} from '@ionic/react';
import { searchOutline, personAddOutline, personOutline, phonePortraitOutline, fileTrayFullOutline, cloudUploadOutline, closeCircle, clipboardOutline, medkitOutline, timeOutline, calendarOutline, refreshOutline } from 'ionicons/icons';
// import { useHistory } from 'react-router-dom';
import api from '../api';
import './RecipientDashboard.css';
import './PatientIntake.css'; // Import Intake CSS for styling

const RecipientDashboard: React.FC = () => {
    const [segment, setSegment] = useState<'search' | 'register' | 'visiting'>('search');
    const [searchText, setSearchText] = useState('');
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [visitingPatients, setVisitingPatients] = useState<any[]>([]);
    const [showTriageModal, setShowTriageModal] = useState(false);
    const [selectedPatient, setSelectedPatient] = useState<any>(null);
    const [toastMsg, setToastMsg] = useState('');
    const [showToast, setShowToast] = useState(false);
    const [usePreferredDoctor, setUsePreferredDoctor] = useState(true);

    // File Upload State
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [uploadedDocuments, setUploadedDocuments] = useState<string[]>([]);
    const [isRefreshing, setIsRefreshing] = useState(false);

    // Symptom Autocomplete
    const [symptomInput, setSymptomInput] = useState('');
    const [symptomSuggestions, setSymptomSuggestions] = useState<any[]>([]);

    useEffect(() => {
        if (segment === 'search') {
            loadInitialPatients();
        } else if (segment === 'visiting') {
            loadVisitingPatients();
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

    const loadVisitingPatients = async () => {
        setIsRefreshing(true);
        try {
            const res = await api.get('/recipient/visiting-patients');
            setVisitingPatients(res.data);
        } catch (err) {
            console.error(err);
            setToastMsg("Failed to load visiting patients");
            setShowToast(true);
        } finally {
            setIsRefreshing(false);
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

    // Chronic Condition Autocomplete
    const [chronicSuggestions, setChronicSuggestions] = useState<any[]>([]);

    const handleChronicSearch = async (val: string) => {
        if (val.length < 2) {
            setChronicSuggestions([]);
            return;
        }
        try {
            const res = await api.get(`/master/chronic-conditions?q=${val}`);
            setChronicSuggestions(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const addChronic = (name: string, isFromReg: boolean) => {
        if (isFromReg) {
            const current = regForm.pre_existing_conditions ? regForm.pre_existing_conditions.split(',').map(s => s.trim()).filter(s => s) : [];
            if (!current.includes(name)) {
                setRegForm({ ...regForm, pre_existing_conditions: [...current, name].join(', ') });
            }
        } else {
            const current = triageForm.chronic_conditions ? triageForm.chronic_conditions.split(',').map(s => s.trim()).filter(s => s) : [];
            if (!current.includes(name)) {
                setTriageForm({ ...triageForm, chronic_conditions: [...current, name].join(', ') });
            }
        }
        setChronicSuggestions([]);
    };

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

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setUploading(true);
            const data = new FormData();
            data.append('file', file);
            try {
                const res = await api.post('/documents/upload', data, { headers: { 'Content-Type': undefined } });
                const { file_path, detected_conditions } = res.data;
                setUploadedFile(file);
                setUploadedDocuments(prev => [...prev, file_path]);

                const newSymptoms = detected_conditions.symptoms || [];
                const newConditions = detected_conditions.chronic_conditions || [];

                if (newSymptoms.length > 0) {
                    const currentSyms = regForm.symptoms ? regForm.symptoms.split(',').map(s => s.trim()).filter(s => s) : [];
                    const updatedSyms = [...new Set([...currentSyms, ...newSymptoms])].join(', ');
                    setRegForm(prev => ({ ...prev, symptoms: updatedSyms }));
                    setToastMsg(`AI Detected Symptoms: ${newSymptoms.join(', ')}`);
                    setShowToast(true);
                }
                if (newConditions.length > 0) {
                    const currentConds = regForm.pre_existing_conditions ? regForm.pre_existing_conditions.split(',').map(s => s.trim()).filter(s => s) : [];
                    const updatedConds = [...new Set([...currentConds, ...newConditions])].join(', ');
                    setRegForm(prev => ({ ...prev, pre_existing_conditions: updatedConds }));
                }
            } catch (err) {
                console.error(err);
                setToastMsg('File upload failed.');
                setShowToast(true);
            } finally {
                setUploading(false);
            }
        }
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
            // Create patient and visit in one go
            const systolicBP = parseInt(regForm.blood_pressure.split('/')[0]) || 120;
            const payload = {
                full_name: regForm.full_name,
                phone_number: regForm.phone_number,
                age: parseInt(regForm.age),
                gender: regForm.gender,
                systolic_bp: systolicBP,
                heart_rate: parseInt(regForm.heart_rate),
                temperature: parseFloat(regForm.temperature),
                symptoms: regForm.symptoms.split(',').map(s => s.trim()).filter(s => s),
                chronic_conditions: regForm.pre_existing_conditions.split(',').map(s => s.trim()).filter(s => s),
                visit_type: 'Walk-In',
                use_preferred_doctor: true,
                uploaded_documents: uploadedDocuments
            };

            await api.post('/visits', payload);
            setToastMsg('Patient Registered & Assigned Successfully!');
            setShowToast(true);

            // Reset form
            setRegForm({
                full_name: '', age: '', gender: 'Male', phone_number: '',
                symptoms: '', blood_pressure: '120/80', heart_rate: '72', temperature: '37.0',
                pre_existing_conditions: ''
            });

            // Switch to visiting tab to see results
            setSegment('visiting');
            loadVisitingPatients();
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
                age: parseInt(selectedPatient.age),
                gender: selectedPatient.gender,
                systolic_bp: parseInt(String(triageForm.systolic_bp)),
                heart_rate: parseInt(String(triageForm.heart_rate)),
                temperature: parseFloat(String(triageForm.temperature)),
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


            <IonContent className="ion-padding">
                <h1 className="page-title">Triage Officer Dashboard</h1>
                <IonSegment value={segment} onIonChange={(e: any) => setSegment(e.detail.value as any)} className="role-segment" mode="ios">
                    <IonSegmentButton value="search" layout="icon-start">
                        <IonIcon icon={searchOutline} />
                        <IonLabel>Search Patient</IonLabel>
                    </IonSegmentButton>
                    <IonSegmentButton value="register" layout="icon-start">
                        <IonIcon icon={personAddOutline} />
                        <IonLabel>New Patient</IonLabel>
                    </IonSegmentButton>
                    <IonSegmentButton value="visiting" layout="icon-start">
                        <IonIcon icon={fileTrayFullOutline} />
                        <IonLabel>Visiting Patients</IonLabel>
                    </IonSegmentButton>
                </IonSegment>

                {segment === 'search' && (
                    <div className="search-section">
                        <IonSearchbar
                            value={searchText}
                            onIonInput={(e: any) => handleSearch(e.detail.value!)}
                            debounce={300}
                            placeholder="🔍 Search by Name or Phone..."
                            className="custom-search"
                            style={{ '--box-shadow': '0 4px 12px rgba(0,0,0,0.05)', '--border-radius': '12px', marginBottom: '1.5rem' }}
                        />

                        <div className="search-results-container">
                            <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#6c757d', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                                Results ({searchResults.length})
                            </h3>

                            {searchResults.length === 0 && (
                                <div style={{ textAlign: 'center', padding: '3rem', color: '#999', background: '#fff', borderRadius: '16px', border: '1px dashed #eee' }}>
                                    <IonIcon icon={searchOutline} style={{ fontSize: '3rem', marginBottom: '0.5rem', opacity: 0.3 }} />
                                    <p style={{ fontSize: '1.1rem' }}>No patients found</p>
                                    <p style={{ fontSize: '0.9rem' }}>Try searching by name or phone number</p>
                                </div>
                            )}

                            {searchResults.map((p, idx) => (
                                <div key={p.patient_id} className="patient-search-card animate-card" style={{ animationDelay: `${idx * 0.05}s` }} onClick={() => openTriage(p)}>
                                    <div style={{ display: 'flex', alignItems: 'center' }}>
                                        <div className="avatar-initials">{p.full_name ? p.full_name.charAt(0) : '?'}</div>
                                        <div className="search-info">
                                            <h2>{p.full_name}</h2>
                                            <p style={{ marginBottom: '4px' }}>
                                                <IonIcon icon={phonePortraitOutline} style={{ fontSize: '1rem' }} />
                                                <span style={{ fontWeight: '500', color: '#495057' }}>{p.phone_number}</span>
                                            </p>
                                            <p>
                                                <span style={{ background: '#f8f9fa', padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem', marginRight: '8px' }}>{p.gender}, {p.age}y</span>
                                                {p.risk_level && <span style={{ color: p.risk_level === 'High' ? '#e53935' : p.risk_level === 'Medium' ? '#fb8c00' : '#43a047', fontWeight: '600', fontSize: '0.85rem' }}>Risk: {p.risk_level}</span>}
                                            </p>
                                        </div>
                                    </div>

                                    {p.current_visit ? (
                                        <div className="current-visit-badge">
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ fontSize: '0.7rem', color: '#1976d2', fontWeight: '700', letterSpacing: '0.5px' }}>ACTIVE VISIT</div>
                                                <div style={{ color: '#0d47a1', fontWeight: '600' }}>{p.current_visit.doctor_name}</div>
                                                <div style={{ fontSize: '0.8rem', color: '#546e7a' }}>{p.current_visit.department}</div>
                                            </div>
                                            <IonIcon icon={medkitOutline} style={{ fontSize: '1.5rem', marginLeft: '8px' }} />
                                        </div>
                                    ) : (
                                        <div style={{ padding: '8px 16px', background: '#f8f9fa', borderRadius: '20px', color: '#adb5bd', fontSize: '0.85rem', fontWeight: '500' }}>
                                            No Active Visit
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {segment === 'register' && (
                    <div className="intake-container">
                        <div className="section-header">
                            <IonIcon icon={personAddOutline} className="section-icon" />
                            <h2>Patient Registration & Triage</h2>
                        </div>

                        {/* File Upload Section */}
                        <div className="upload-section" style={{ marginBottom: '2rem' }}>
                            <label className="section-label">UPLOAD HEALTH DOCUMENT (OCR)</label>
                            <div className="upload-box" style={{ border: '2px dashed var(--color-primary-light)', padding: '2rem', textAlign: 'center', borderRadius: '12px', background: 'rgba(56, 128, 255, 0.05)', position: 'relative' }}>
                                <input type="file" id="file-upload" accept=".jpg,.png,.pdf" onChange={handleFileUpload} style={{ display: 'none' }} />
                                <label htmlFor="file-upload" style={{ display: 'block', cursor: 'pointer', width: '100%' }}>
                                    <IonIcon icon={cloudUploadOutline} style={{ fontSize: '3rem', color: 'var(--color-primary)' }} />
                                    <p style={{ margin: '0.5rem 0', fontWeight: 'bold', color: 'var(--color-primary)' }}>{uploading ? 'Analyzing...' : 'Click to Upload Report / ID'}</p>
                                    <span style={{ fontSize: '0.8rem', color: '#666' }}>Auto-fills details from document</span>
                                </label>
                                {uploadedFile && (
                                    <div style={{ marginTop: '1rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'white', padding: '8px 16px', borderRadius: '20px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)' }}>
                                        <span>📄 {uploadedFile.name}</span>
                                        <IonIcon icon={closeCircle} onClick={() => { setUploadedFile(null); setUploadedDocuments([]) }} style={{ cursor: 'pointer', color: 'var(--color-danger)', fontSize: '1.2rem' }} />
                                    </div>
                                )}
                            </div>
                        </div>

                        <IonGrid>
                            <IonRow>
                                <IonCol size="12" sizeMd="6">
                                    <div className="form-group">
                                        <label>FULL NAME *</label>
                                        <IonInput value={regForm.full_name} onIonChange={(e: any) => setRegForm({ ...regForm, full_name: e.detail.value! })} className="custom-input" placeholder="e.g. John Doe" />
                                    </div>
                                </IonCol>
                                <IonCol size="12" sizeMd="6">
                                    <div className="form-group">
                                        <label>PHONE NUMBER *</label>
                                        <IonInput type="tel" value={regForm.phone_number} onIonChange={(e: any) => setRegForm({ ...regForm, phone_number: e.detail.value! })} className="custom-input" placeholder="e.g. 9876543210" />
                                    </div>
                                </IonCol>
                                <IonCol size="6" sizeMd="3">
                                    <div className="form-group">
                                        <label>AGE *</label>
                                        <IonInput type="number" value={regForm.age} onIonChange={(e: any) => setRegForm({ ...regForm, age: e.detail.value! })} className="custom-input" placeholder="Age" />
                                    </div>
                                </IonCol>
                                <IonCol size="6" sizeMd="3">
                                    <div className="form-group">
                                        <label>GENDER</label>
                                        <IonSelect value={regForm.gender} onIonChange={(e: any) => setRegForm({ ...regForm, gender: e.detail.value })} className="custom-select" interface="popover">
                                            <IonSelectOption value="Male">Male</IonSelectOption>
                                            <IonSelectOption value="Female">Female</IonSelectOption>
                                            <IonSelectOption value="Other">Other</IonSelectOption>
                                        </IonSelect>
                                    </div>
                                </IonCol>
                            </IonRow>

                            <IonRow>
                                <IonCol size="4">
                                    <div className="form-group">
                                        <label>SYSTOLIC BP</label>
                                        <IonInput type="number" value={regForm.blood_pressure.split('/')[0]} onIonChange={(e: any) => setRegForm({ ...regForm, blood_pressure: `${e.detail.value!}/80` })} className="custom-input" placeholder="120" />
                                    </div>
                                </IonCol>
                                <IonCol size="4">
                                    <div className="form-group">
                                        <label>HEART RATE</label>
                                        <IonInput type="number" value={regForm.heart_rate} onIonChange={(e: any) => setRegForm({ ...regForm, heart_rate: e.detail.value! })} className="custom-input" placeholder="72" />
                                    </div>
                                </IonCol>
                                <IonCol size="4">
                                    <div className="form-group">
                                        <label>TEMP (°C)</label>
                                        <IonInput type="number" value={regForm.temperature} onIonChange={(e: any) => setRegForm({ ...regForm, temperature: e.detail.value! })} className="custom-input" placeholder="37.0" />
                                    </div>
                                </IonCol>
                            </IonRow>
                        </IonGrid>

                        <div className="symptoms-section">
                            <label className="section-label">SYMPTOMS / CHIEF COMPLAINT *</label>
                            <div className="custom-input-wrapper" style={{ border: '1px solid #ddd', borderRadius: '12px', padding: '0 10px', marginBottom: '10px', display: 'flex', alignItems: 'center', background: 'white' }}>
                                <IonIcon icon={searchOutline} color="medium" />
                                <IonInput value={symptomInput} onIonInput={(e: any) => handleSymptomSearch(e.detail.value!)} placeholder="Type to search symptoms..." style={{ '--padding-start': '10px' }} />
                            </div>

                            {symptomSuggestions.length > 0 && (
                                <IonList className="autocomplete-list" style={{ border: '1px solid #eee', borderRadius: '8px', marginBottom: '1rem' }}>
                                    {symptomSuggestions.map((s, idx) => (
                                        <IonItem key={idx} button onClick={() => addSymptom(s.name, true)} lines="none">
                                            <IonLabel>{s.name}</IonLabel>
                                        </IonItem>
                                    ))}
                                </IonList>
                            )}
                            <IonTextarea value={regForm.symptoms} readonly className="custom-textarea" rows={2} placeholder="Selected symptoms..." style={{ background: '#f9f9f9', padding: '10px', borderRadius: '12px', border: '1px solid #eee' }} />
                        </div>

                        <div className="conditions-section">
                            <label className="section-label">CHRONIC CONDITIONS</label>
                            <div className="custom-input-wrapper" style={{ border: '1px solid #ddd', borderRadius: '12px', padding: '0 10px', marginBottom: '10px', display: 'flex', alignItems: 'center', background: 'white' }}>
                                <IonIcon icon={searchOutline} color="medium" />
                                <IonInput onIonInput={(e: any) => handleChronicSearch(e.detail.value!)} placeholder="Type to search conditions..." style={{ '--padding-start': '10px' }} />
                            </div>

                            {chronicSuggestions.length > 0 && (
                                <IonList className="autocomplete-list" style={{ border: '1px solid #eee', borderRadius: '8px', marginBottom: '1rem' }}>
                                    {chronicSuggestions.map((c: any, idx) => (
                                        <IonItem key={idx} button onClick={() => addChronic(c.name, true)} lines="none">
                                            <IonLabel>{c.name} <IonNote slot="end">Risk: {c.risk_modifier}</IonNote></IonLabel>
                                        </IonItem>
                                    ))}
                                </IonList>
                            )}
                            <IonTextarea value={regForm.pre_existing_conditions} readonly className="custom-textarea" rows={2} placeholder="Selected conditions..." style={{ background: '#f9f9f9', padding: '10px', borderRadius: '12px', border: '1px solid #eee' }} />
                        </div>

                        <div className="submit-section" style={{ marginTop: '3rem' }}>
                            <IonButton expand="block" shape="round" className="run-triage-btn" onClick={handleRegister} style={{ height: '56px', fontSize: '1.1rem', fontWeight: '700', '--box-shadow': '0 10px 20px rgba(56, 128, 255, 0.3)' }}>
                                <IonIcon icon={personAddOutline} slot="start" />
                                Register & Assign Doctor
                            </IonButton>
                        </div>
                    </div>
                )}

                {segment === 'visiting' && (
                    <div className="visiting-section-container">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '600', color: '#6c757d', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                                Visiting Patients ({visitingPatients.length})
                            </h3>
                            <IonButton fill="clear" size="small" onClick={loadVisitingPatients} color="medium" disabled={isRefreshing}>
                                <IonIcon icon={refreshOutline} slot="start" className={isRefreshing ? 'spin-icon' : ''} /> Refresh
                            </IonButton>
                        </div>

                        {visitingPatients.length === 0 && (
                            <div className="empty-queue" style={{ textAlign: 'center', padding: '3rem', background: 'white', borderRadius: '16px' }}>
                                <IonIcon icon={fileTrayFullOutline} style={{ fontSize: '3rem', color: '#dee2e6' }} />
                                <h3 style={{ color: '#6c757d' }}>No Assigned Patients</h3>
                                <p style={{ color: '#adb5bd' }}>Patients will appear here once assigned to a doctor.</p>
                            </div>
                        )}

                        <IonGrid style={{ padding: 0 }}>
                            <IonRow>
                                {visitingPatients.map((p, idx) => (
                                    <IonCol size="12" sizeMd="6" sizeLg="4" key={idx} className="animate-card" style={{ animationDelay: `${idx * 0.1}s` }}>
                                        <div className="visiting-patient-card">
                                            <div className="visiting-header">
                                                <h4 className="visiting-name">{p.patient_name}</h4>
                                                <span className={`risk-badge ${p.risk_level || 'Low'}`}>{p.risk_level || 'Normal'} Risk</span>
                                            </div>
                                            <div className="visiting-body">
                                                <div className="doctor-info-row">
                                                    <div className="doctor-avatar"><IonIcon icon={medkitOutline} /></div>
                                                    <div>
                                                        <div style={{ fontSize: '0.7rem', color: '#999', fontWeight: '700', textTransform: 'uppercase' }}>Assigned To</div>
                                                        <div style={{ fontWeight: '700', color: 'var(--color-navy-dark)', fontSize: '0.95rem' }}>{p.doctor_name}</div>
                                                        <div style={{ fontSize: '0.8rem', color: 'var(--color-primary)', fontWeight: '500' }}>{p.department}</div>
                                                    </div>
                                                </div>

                                                <div className="clinical-notes">
                                                    <div style={{ fontSize: '0.7rem', color: '#6c757d', fontWeight: '700', textTransform: 'uppercase', marginBottom: '4px' }}>Clinical Findings</div>
                                                    <p style={{ margin: 0, fontStyle: 'italic', fontSize: '0.9rem', color: '#495057' }}>"{p.symptoms}"</p>
                                                </div>

                                                <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', color: '#adb5bd', paddingTop: '1rem', borderTop: '1px solid #f8f9fa' }}>
                                                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><IonIcon icon={calendarOutline} /> {p.patient_details}</span>
                                                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><IonIcon icon={timeOutline} /> {p.visit_time || 'Just now'}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </IonCol>
                                ))}
                            </IonRow>
                        </IonGrid>
                    </div>
                )}

                <IonModal className="triage-modal-custom" isOpen={showTriageModal} onDidDismiss={() => setShowTriageModal(false)} style={{ '--border-radius': '20px', '--max-height': '90%' }}>
                    <IonHeader className="ion-no-border">
                        <IonToolbar style={{ '--background': 'var(--color-navy-dark)', '--color': 'white' }}>
                            <IonTitle style={{ fontWeight: '700' }}>Start Patient Visit</IonTitle>
                            <IonButtons slot="end">
                                <IonButton onClick={() => setShowTriageModal(false)}>
                                    <IonIcon icon={closeCircle} style={{ fontSize: '1.8rem' }} />
                                </IonButton>
                            </IonButtons>
                        </IonToolbar>
                    </IonHeader>
                    <IonContent className="ion-padding" style={{ '--background': '#f8f9fa' }}>
                        <div className="intake-container" style={{ padding: '0', boxShadow: 'none', background: 'transparent' }}>
                            {selectedPatient && (
                                <div style={{ background: 'white', borderRadius: '16px', padding: '1.5rem', marginBottom: '1.5rem', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                    <div className="avatar-initials" style={{ width: '60px', height: '60px', fontSize: '1.5rem' }}>{selectedPatient.full_name.charAt(0)}</div>
                                    <div>
                                        <h2 style={{ margin: '0 0 5px 0', fontSize: '1.4rem', color: 'var(--color-navy-dark)' }}>{selectedPatient.full_name}</h2>
                                        <div style={{ display: 'flex', gap: '15px', color: '#666', fontSize: '0.95rem' }}>
                                            <span><IonIcon icon={personOutline} style={{ verticalAlign: 'middle', marginRight: '4px' }} /> {selectedPatient.gender}, {selectedPatient.age}y</span>
                                            <span><IonIcon icon={phonePortraitOutline} style={{ verticalAlign: 'middle', marginRight: '4px' }} /> {selectedPatient.phone_number}</span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div style={{ background: 'white', borderRadius: '16px', padding: '1.5rem', marginBottom: '1.5rem', boxShadow: '0 2px 8px rgba(0,0,0,0.03)' }}>
                                <h3 className="section-title" style={{ marginTop: 0 }}>Vital Signs</h3>
                                <IonGrid style={{ padding: 0 }}>
                                    <IonRow>
                                        <IonCol size="4">
                                            <div className="form-group">
                                                <label>Systolic BP</label>
                                                <IonInput type="number" value={triageForm.systolic_bp} onIonChange={(e: any) => setTriageForm({ ...triageForm, systolic_bp: parseInt(e.detail.value!, 10) })} className="custom-input" placeholder="120" />
                                            </div>
                                        </IonCol>
                                        <IonCol size="4">
                                            <div className="form-group">
                                                <label>Heart Rate</label>
                                                <IonInput type="number" value={triageForm.heart_rate} onIonChange={(e: any) => setTriageForm({ ...triageForm, heart_rate: parseInt(e.detail.value!, 10) })} className="custom-input" placeholder="72" />
                                            </div>
                                        </IonCol>
                                        <IonCol size="4">
                                            <div className="form-group">
                                                <label>Temp (°C)</label>
                                                <IonInput type="number" value={triageForm.temperature} onIonChange={(e: any) => setTriageForm({ ...triageForm, temperature: parseFloat(e.detail.value!) })} className="custom-input" placeholder="37.0" />
                                            </div>
                                        </IonCol>
                                    </IonRow>
                                </IonGrid>
                            </div>

                            <div style={{ background: 'white', borderRadius: '16px', padding: '1.5rem', marginBottom: '1.5rem', boxShadow: '0 2px 8px rgba(0,0,0,0.03)' }}>
                                <h3 className="section-title" style={{ marginTop: 0 }}>Clinical Assessment</h3>

                                <div className="form-group">
                                    <label>Add Symptoms</label>
                                    <div className="custom-input-wrapper" style={{ border: '1px solid #ddd', borderRadius: '12px', padding: '0 10px', marginBottom: '10px', display: 'flex', alignItems: 'center' }}>
                                        <IonIcon icon={searchOutline} color="medium" />
                                        <IonInput value={symptomInput} onIonInput={(e: any) => handleSymptomSearch(e.detail.value!)} placeholder="Type to search..." style={{ '--padding-start': '10px' }} />
                                    </div>
                                    {symptomSuggestions.length > 0 && (
                                        <IonList className="autocomplete-list" style={{ border: '1px solid #eee', borderRadius: '8px', marginBottom: '1rem' }}>
                                            {symptomSuggestions.map((s, idx) => (
                                                <IonItem key={idx} button onClick={() => addSymptom(s.name, false)} lines="none">
                                                    <IonLabel>{s.name}</IonLabel>
                                                </IonItem>
                                            ))}
                                        </IonList>
                                    )}
                                    <IonTextarea value={triageForm.symptoms} onIonChange={(e: any) => setTriageForm({ ...triageForm, symptoms: e.detail.value! })} className="custom-textarea" rows={3} placeholder="Patient's chief complaints..." style={{ background: '#f9f9f9', padding: '10px', borderRadius: '12px', border: '1px solid #eee' }} />
                                </div>

                                <div className="form-group" style={{ marginTop: '1.5rem' }}>
                                    <label>Chronic Conditions</label>
                                    <IonTextarea value={triageForm.chronic_conditions} onIonChange={(e: any) => setTriageForm({ ...triageForm, chronic_conditions: e.detail.value! })} className="custom-textarea" rows={2} placeholder="Any pre-existing conditions..." style={{ background: '#f9f9f9', padding: '10px', borderRadius: '12px', border: '1px solid #eee' }} />
                                </div>
                            </div>

                            <div style={{ background: 'white', borderRadius: '16px', padding: '1.5rem', marginBottom: '1.5rem', boxShadow: '0 2px 8px rgba(0,0,0,0.03)' }}>
                                <h3 className="section-title" style={{ marginTop: 0 }}>Visit Details</h3>
                                <IonGrid style={{ padding: 0 }}>
                                    <IonRow>
                                        <IonCol size="6">
                                            <div className="form-group">
                                                <label>Visit Priority</label>
                                                <IonSelect value={triageForm.visit_type} onIonChange={(e: any) => setTriageForm({ ...triageForm, visit_type: e.detail.value })} className="custom-select" interface="popover">
                                                    <IonSelectOption value="Walk-In">Walk-In (Normal)</IonSelectOption>
                                                    <IonSelectOption value="Emergency">Emergency</IonSelectOption>
                                                    <IonSelectOption value="Follow-up">Follow-up</IonSelectOption>
                                                </IonSelect>
                                            </div>
                                        </IonCol>
                                        <IonCol size="6">
                                            <div className="form-group">
                                                <label>Doctor Preference</label>
                                                <div style={{ display: 'flex', alignItems: 'center', height: '50px', background: '#f8f9fa', borderRadius: '12px', padding: '0 1rem', border: '1px solid #ddd' }}>
                                                    <IonLabel style={{ flex: 1, color: '#555', fontSize: '0.9rem' }}>Use Previous Doctor</IonLabel>
                                                    <IonToggle checked={usePreferredDoctor} onIonChange={(e: any) => setUsePreferredDoctor(e.detail.checked)} />
                                                </div>
                                            </div>
                                        </IonCol>
                                    </IonRow>
                                </IonGrid>
                            </div>

                            <IonButton expand="block" shape="round" className="run-triage-btn" onClick={handleTriageSubmit} style={{ height: '56px', fontSize: '1.1rem', fontWeight: '700', '--box-shadow': '0 10px 20px rgba(45, 211, 111, 0.3)', '--background': 'var(--color-success)' }}>
                                <IonIcon icon={medkitOutline} slot="start" />
                                Admit & Assign Doctor
                            </IonButton>
                        </div>
                    </IonContent>
                </IonModal>

                <IonToast isOpen={showToast} onDidDismiss={() => setShowToast(false)} message={toastMsg} duration={2000} color="dark" />
            </IonContent>
        </IonPage>
    );
};

export default RecipientDashboard;
