"""
Tests para modelos de base de datos
"""
import pytest
from datetime import datetime
from app.models.user import User
from app.models.academic import AcademicYear, Period, Grade, Group, Subgroup
from app.models.student import Student


@pytest.mark.unit
@pytest.mark.models
class TestUserModel:
    """Tests para el modelo User"""
    
    def test_create_user(self, db_session):
        """Test crear usuario básico"""
        user = User(
            username="newuser",
            email="newuser@example.com",
            full_name="New User",
            is_active=True,
            is_superuser=False
        )
        user.set_password("Password123")
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.password_hash is not None
        assert user.password_hash != "Password123"  # No debe guardarse en texto plano
    
    def test_password_hashing(self, db_session):
        """Test que la contraseña se hashea con Argon2id"""
        user = User(
            username="hashtest",
            email="hashtest@example.com",
            full_name="Hash Test"
        )
        user.set_password("MySecretPassword123")
        
        # Verificar que el hash empieza con $argon2id$ (Argon2id)
        assert user.password_hash.startswith("$argon2id$")
    
    def test_password_verification(self, db_session):
        """Test verificación de contraseña"""
        user = User(
            username="verifytest",
            email="verifytest@example.com",
            full_name="Verify Test"
        )
        password = "VerifyPassword123"
        user.set_password(password)
        
        # Contraseña correcta
        assert user.verify_password(password) is True
        
        # Contraseña incorrecta
        assert user.verify_password("WrongPassword") is False
    
    def test_user_timestamps(self, db_session):
        """Test que se crean timestamps automáticamente"""
        user = User(
            username="timetest",
            email="timetest@example.com",
            full_name="Time Test"
        )
        user.set_password("Password123")
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)


@pytest.mark.unit
@pytest.mark.models
class TestAcademicModels:
    """Tests para modelos académicos"""
    
    def test_create_academic_year(self, db_session):
        """Test crear año académico"""
        year = AcademicYear(
            year=2026,
            name="Año Académico 2026",
            is_active=True
        )
        
        db_session.add(year)
        db_session.commit()
        db_session.refresh(year)
        
        assert year.id is not None
        assert year.year == 2026
        assert year.is_active is True
    
    def test_academic_hierarchy(self, db_session):
        """Test jerarquía completa académica"""
        # Año académico
        year = AcademicYear(year=2026, name="2026", is_active=True)
        db_session.add(year)
        db_session.commit()
        
        # Grado
        grade = Grade(
            academic_year_id=year.id,
            name="7mo Grado",
            level=7
        )
        db_session.add(grade)
        db_session.commit()
        
        # Grupo
        group = Group(
            grade_id=grade.id,
            name="Sección A"
        )
        db_session.add(group)
        db_session.commit()
        
        # Subgrupo
        subgroup = Subgroup(
            group_id=group.id,
            name="Equipo 1"
        )
        db_session.add(subgroup)
        db_session.commit()
        
        # Verificar relaciones
        db_session.refresh(year)
        assert len(year.grades) == 1
        assert year.grades[0].groups[0].subgroups[0].name == "Equipo 1"
    
    def test_unique_constraints(self, db_session):
        """Test que los constraints únicos funcionan"""
        year = AcademicYear(year=2026, name="2026", is_active=True)
        db_session.add(year)
        db_session.commit()
        
        # Intentar crear otro año con mismo número
        duplicate_year = AcademicYear(year=2026, name="2026 Duplicate", is_active=False)
        db_session.add(duplicate_year)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


@pytest.mark.unit
@pytest.mark.models
class TestStudentModel:
    """Tests para el modelo Student"""
    
    def test_create_student(self, db_session):
        """Test crear estudiante"""
        # Crear jerarquía mínima
        year = AcademicYear(year=2026, name="2026", is_active=True)
        db_session.add(year)
        db_session.commit()
        
        grade = Grade(academic_year_id=year.id, name="7mo", level=7)
        db_session.add(grade)
        db_session.commit()
        
        group = Group(grade_id=grade.id, name="A")
        db_session.add(group)
        db_session.commit()
        
        subgroup = Subgroup(group_id=group.id, name="Equipo 1")
        db_session.add(subgroup)
        db_session.commit()
        
        # Crear estudiante
        from datetime import date
        student = Student(
            identification="123456789",
            first_name="Juan",
            last_name="Pérez",
            date_of_birth=date(2012, 5, 15),
            subgroup_id=subgroup.id,
            is_active=True
        )
        
        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)
        
        assert student.id is not None
        assert student.full_name == "Juan Pérez"
        assert student.subgroup.name == "Equipo 1"
