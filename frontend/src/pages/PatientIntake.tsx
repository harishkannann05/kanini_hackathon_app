import React, { useState } from 'react';
import {
    IonContent, IonHeader, IonPage, IonTitle, IonToolbar,
    IonButton, IonLabel, IonInput, IonSelect, IonSelectOption,
    IonChip, IonIcon, IonGrid, IonRow, IonCol
} from '@ionic/react';
import { cloudUploadOutline, closeCircle } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import api from '../api';
import './PatientIntake.css';

const SYMPTOMS = [
    'Chest Pain', 'Shortness of Breath', 'Fever', 'Headache', 'Dizziness',
    'Cough', 'Vomiting', 'Abdominal Pain', 'Palpitations', 'Weakness', 'Numbness', 'Diarrhea'
];

const CONDITIONS = [
    'Hypertension', 'Diabetes', 'Heart Disease', 'Asthma', 'Chronic Kidney Disease'
];

const PatientIntake: React.FC = () => {
    const history = useHistory();
    const [formData, setFormData] = useState({
        age: '',
        gender: 'Male',
        systolic_bp: '',
        heart_rate: '',
        temperature: '',
        visit_type: 'Walk-In'
    });
    const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
    const [selectedConditions, setSelectedConditions] = useState<string[]>([]);
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);

    const [uploadedDocuments, setUploadedDocuments] = useState<string[]>([]);
    const [uploading, setUploading] = useState(false);

    const toggleSymptom = (symptom: string) => {
        setSelectedSymptoms(prev =>
            prev.includes(symptom)
                ? prev.filter(s => s !== symptom)
                : [...prev, symptom]
        );
    };

    const toggleCondition = (condition: string) => {
        setSelectedConditions(prev =>
            prev.includes(condition)
                ? prev.filter(c => c !== condition)
                : [...prev, condition]
        );
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setUploading(true);

            const data = new FormData();
            data.append('file', file);

            try {
                // Let browser set the Content-Type with boundary for FormData
                const res = await api.post('/documents/upload', data, {
                    headers: { 'Content-Type': undefined }
                });

                const { file_path, detected_conditions } = res.data;
                setUploadedFile(file);
                setUploadedDocuments(prev => [...prev, file_path]);

                // Auto-fill from OCR
                const newSymptoms = detected_conditions.symptoms || [];
                const newConditions = detected_conditions.chronic_conditions || [];

                if (newSymptoms.length > 0) {
                    setSelectedSymptoms(prev => [...new Set([...prev, ...newSymptoms])]);
                    alert(`AI Detected Symptoms: ${newSymptoms.join(', ')}`);
                }

                if (newConditions.length > 0) {
                    setSelectedConditions(prev => [...new Set([...prev, ...newConditions])]);
                    alert(`AI Detected Conditions: ${newConditions.join(', ')}`);
                }

            } catch (err: any) {
                console.error(err);
                alert('File upload failed.');
            } finally {
                setUploading(false);
            }
        }
    };

    const handleSubmit = async () => {
        try {
            const payload = {
                age: parseInt(formData.age) || 0,
                gender: formData.gender,
                symptoms: selectedSymptoms,
                systolic_bp: parseInt(formData.systolic_bp) || 120,
                heart_rate: parseInt(formData.heart_rate) || 80,
                temperature: parseFloat(formData.temperature) || 98.6,
                visit_type: formData.visit_type, // "Walk-In"
                chronic_conditions: selectedConditions,
                uploaded_documents: uploadedDocuments
            };

            const res = await api.post('/visits', payload);
            console.log('Triage Result:', res.data);
            history.push('/dashboard');
        } catch (err: any) {
            console.error(err);
            const detail = err.response?.data?.detail;
            let message = 'Failed to submit intake.';

            if (typeof detail === 'string') {
                message = detail;
            } else if (Array.isArray(detail)) {
                message = detail.map((e: any) => `${e.loc[1]}: ${e.msg}`).join('\n');
            } else if (typeof detail === 'object') {
                message = JSON.stringify(detail);
            }

            alert(message);
        }
    };

    return (
        <IonPage className="patient-intake-page">
            <IonHeader>
                <IonToolbar className="custom-toolbar">
                    <IonTitle className="custom-title" onClick={() => history.push('/')} style={{ cursor: 'pointer' }}>
                        <span className="logo-icon">🏥</span> AI Smart Triage
                    </IonTitle>
                    <div slot="end" className="nav-buttons">
                        <IonButton fill="clear" routerLink="/" className="nav-btn">
                            Home
                        </IonButton>
                        <IonButton fill="clear" routerLink="/intake" className="active-nav">
                            Patient Intake
                        </IonButton>
                        <IonButton fill="clear" routerLink="/dashboard">
                            Dashboard
                        </IonButton>
                        <IonButton fill="clear" routerLink="/doctors">
                            Doctors
                        </IonButton>
                    </div>
                </IonToolbar>
            </IonHeader>

            <IonContent className="dark-content">
                <div className="intake-container">
                    <div className="section-header">
                        <IonIcon icon={cloudUploadOutline} className="section-icon" />
                        <h2>Patient Information</h2>
                    </div>

                    <IonGrid>
                        <IonRow>
                            <IonCol size="12" sizeMd="3">
                                <div className="form-group">
                                    <label>AGE</label>
                                    <IonInput
                                        type="number"
                                        placeholder="e.g. 45"
                                        value={formData.age}
                                        onIonChange={e => setFormData({ ...formData, age: e.detail.value! })}
                                        className="custom-input"
                                    />
                                </div>
                            </IonCol>
                            <IonCol size="12" sizeMd="3">
                                <div className="form-group">
                                    <label>GENDER</label>
                                    <IonSelect
                                        value={formData.gender}
                                        onIonChange={e => setFormData({ ...formData, gender: e.detail.value! })}
                                        className="custom-select"
                                    >
                                        <IonSelectOption value="Male">Male</IonSelectOption>
                                        <IonSelectOption value="Female">Female</IonSelectOption>
                                        <IonSelectOption value="Other">Other</IonSelectOption>
                                    </IonSelect>
                                </div>
                            </IonCol>
                            <IonCol size="12" sizeMd="2">
                                <div className="form-group">
                                    <label>SYSTOLIC BP (MMHG)</label>
                                    <IonInput
                                        type="number"
                                        placeholder="e.g. 120"
                                        value={formData.systolic_bp}
                                        onIonChange={e => setFormData({ ...formData, systolic_bp: e.detail.value! })}
                                        className="custom-input"
                                    />
                                </div>
                            </IonCol>
                            <IonCol size="12" sizeMd="2">
                                <div className="form-group">
                                    <label>HEART RATE (BPM)</label>
                                    <IonInput
                                        type="number"
                                        placeholder="e.g. 80"
                                        value={formData.heart_rate}
                                        onIonChange={e => setFormData({ ...formData, heart_rate: e.detail.value! })}
                                        className="custom-input"
                                    />
                                </div>
                            </IonCol>
                            <IonCol size="12" sizeMd="2">
                                <div className="form-group">
                                    <label>TEMPERATURE (°C)</label>
                                    <IonInput
                                        type="number"
                                        placeholder="e.g. 37.5"
                                        value={formData.temperature}
                                        onIonChange={e => setFormData({ ...formData, temperature: e.detail.value! })}
                                        className="custom-input"
                                    />
                                </div>
                            </IonCol>
                        </IonRow>

                        <IonRow>
                            <IonCol size="12" sizeMd="6">
                                <div className="form-group">
                                    <label>VISIT TYPE</label>
                                    <IonSelect
                                        value={formData.visit_type}
                                        onIonChange={e => setFormData({ ...formData, visit_type: e.detail.value! })}
                                        className="custom-select"
                                    >
                                        <IonSelectOption value="Walk-In">Walk-In</IonSelectOption>
                                        <IonSelectOption value="Appointment">Appointment</IonSelectOption>
                                        <IonSelectOption value="Emergency">Emergency</IonSelectOption>
                                    </IonSelect>
                                </div>
                            </IonCol>
                        </IonRow>
                    </IonGrid>

                    <div className="symptoms-section">
                        <label className="section-label">SYMPTOMS (CLICK TO SELECT)</label>
                        <div className="chip-container">
                            {SYMPTOMS.map(symptom => (
                                <IonChip
                                    key={symptom}
                                    onClick={() => toggleSymptom(symptom)}
                                    className={selectedSymptoms.includes(symptom) ? 'chip-selected' : 'chip-unselected'}
                                >
                                    <IonLabel>{symptom}</IonLabel>
                                    {selectedSymptoms.includes(symptom) && <IonIcon icon={closeCircle} />}
                                </IonChip>
                            ))}
                        </div>
                    </div>

                    <div className="conditions-section">
                        <label className="section-label">PRE-EXISTING CONDITIONS</label>
                        <div className="chip-container">
                            {CONDITIONS.map(condition => (
                                <IonChip
                                    key={condition}
                                    onClick={() => toggleCondition(condition)}
                                    className={selectedConditions.includes(condition) ? 'chip-selected' : 'chip-unselected'}
                                >
                                    <IonLabel>{condition}</IonLabel>
                                    {selectedConditions.includes(condition) && <IonIcon icon={closeCircle} />}
                                </IonChip>
                            ))}
                        </div>
                    </div>

                    <div className="upload-section">
                        <label className="section-label">UPLOAD HEALTH DOCUMENT (EHR / EMR)</label>
                        <div className="upload-box">
                            <input
                                type="file"
                                id="file-upload"
                                accept=".jpg,.png,.pdf"
                                onChange={handleFileUpload}
                                style={{ display: 'none' }}
                            />
                            <label htmlFor="file-upload" className="upload-label">
                                <IonIcon icon={cloudUploadOutline} className="upload-icon" />
                                <p>{uploading ? 'Uploading & Analyzing...' : 'Click or drag & drop files here'}</p>
                                <span>Supported: Images (JPG, PNG), PDF</span>
                            </label>
                            {uploadedFile && (
                                <div className="uploaded-file">
                                    <span>📄 {uploadedFile.name}</span>
                                    <IonIcon icon={closeCircle} onClick={() => setUploadedFile(null)} />
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="submit-section">
                        <IonButton
                            expand="block"
                            className="run-triage-btn"
                            onClick={handleSubmit}
                        >
                            ⚡ Run AI Triage
                        </IonButton>
                    </div>
                </div>
            </IonContent>
        </IonPage>
    );
};

export default PatientIntake;
