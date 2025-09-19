import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configuration de l'application
app = Flask(__name__)
# Chemin absolu pour la base de données pour éviter les problèmes
basedir = os.path.abspath(os.path.dirname(__file__))
# Configuration du secret key et de la base de données SQLite
app.config['SECRET_KEY'] = 'une-cle-secrete-difficile-a-deviner'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'evaluations.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Modèles de la base de données ---

class Student(db.Model):
    """Modèle pour un étudiant."""
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    
    # Relation pour accéder facilement aux évaluations d'un étudiant
    evaluations = db.relationship('Evaluation', backref='student', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Student {self.firstname} {self.lastname}>'

class Evaluation(db.Model):
    """Modèle pour une évaluation, basée sur les critères du PDF."""
    id = db.Column(db.Integer, primary_key=True)
    evaluation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Critères d'évaluation (stockés comme des chaînes de caractères)
    non_verbal = db.Column(db.String(5), nullable=False) # Regard, Voix, Gestuelle, Posture
    clarity_articulation = db.Column(db.String(5), nullable=False) # Contenu clair et articulé
    logical_flow = db.Column(db.String(5), nullable=False) # Enchaînement logique
    slides_quality = db.Column(db.String(5), nullable=False) # Qualité du diaporama
    spec_respect = db.Column(db.String(5), nullable=False) # Respect du cahier des charges
    
    # Champ pour les commentaires et axes d'amélioration
    improvement_axes = db.Column(db.Text, nullable=True)
    
    # Clé étrangère pour lier l'évaluation à un étudiant
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    def __repr__(self):
        return f'<Evaluation {self.id} for student {self.student_id}>'

# --- Routes de l'application (les différentes pages) ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """Page d'accueil: affiche la liste des étudiants et permet d'en ajouter."""
    if request.method == 'POST':
        # Logique pour ajouter un nouvel étudiant
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        if firstname and lastname:
            new_student = Student(firstname=firstname, lastname=lastname)
            db.session.add(new_student)
            db.session.commit()
            flash(f'Étudiant {firstname} {lastname} ajouté avec succès !', 'success')
        else:
            flash('Le prénom et le nom sont requis.', 'danger')
        return redirect(url_for('index'))
        
    students = Student.query.order_by(Student.lastname).all()
    return render_template('index.html', students=students)

@app.route('/student/<int:student_id>')
def student_detail(student_id):
    """Affiche les détails et l'historique des évaluations pour un étudiant."""
    student = Student.query.get_or_404(student_id)
    # Ordonner les évaluations de la plus récente à la plus ancienne
    evaluations = sorted(student.evaluations, key=lambda e: e.evaluation_date, reverse=True)
    return render_template('student_detail.html', student=student, evaluations=evaluations)

@app.route('/student/<int:student_id>/add_evaluation', methods=['GET', 'POST'])
def add_evaluation(student_id):
    """Page avec le formulaire pour créer une nouvelle évaluation."""
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        # Récupération des données du formulaire
        new_eval = Evaluation(
            student_id=student.id,
            non_verbal=request.form['non_verbal'],
            clarity_articulation=request.form['clarity_articulation'],
            logical_flow=request.form['logical_flow'],
            slides_quality=request.form['slides_quality'],
            spec_respect=request.form['spec_respect'],
            improvement_axes=request.form['improvement_axes']
        )
        db.session.add(new_eval)
        db.session.commit()
        flash('Évaluation ajoutée avec succès.', 'success')
        return redirect(url_for('student_detail', student_id=student.id))
        
    return render_template('add_evaluation.html', student=student)

@app.route('/student/<int:student_id>/delete', methods=['POST'])
def delete_student(student_id):
    """Route pour supprimer un étudiant et toutes ses évaluations."""
    student_to_delete = Student.query.get_or_404(student_id)
    db.session.delete(student_to_delete)
    db.session.commit()
    flash(f'Étudiant {student_to_delete.firstname} {student_to_delete.lastname} et ses évaluations ont été supprimés.', 'success')
    return redirect(url_for('index'))
    
@app.route('/evaluation/<int:evaluation_id>/delete', methods=['POST'])
def delete_evaluation(evaluation_id):
    """Route pour supprimer une évaluation spécifique."""
    evaluation_to_delete = Evaluation.query.get_or_404(evaluation_id)
    student_id = evaluation_to_delete.student_id
    db.session.delete(evaluation_to_delete)
    db.session.commit()
    flash('L\'évaluation a été supprimée.', 'success')
    return redirect(url_for('student_detail', student_id=student_id))

# --- Initialisation ---
if __name__ == '__main__':
    with app.app_context():
        # Crée le dossier 'instance' s'il n'existe pas
        instance_path = os.path.join(basedir, 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        # Crée les tables dans la base de données si elles n'existent pas
        db.create_all()
    app.run(debug=True)