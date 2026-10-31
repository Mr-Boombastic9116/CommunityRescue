from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.donor import Donor
from app.models.ngo import NGOPartner
from app.models.volunteer import Volunteer
from app.schemas.user import UserRegister, UserLogin, Token, UserProfileResponse, ProfileUpdate
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Check if email is already taken
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    try:
        # Create core User
        new_user = User(
            name=user_in.name,
            email=user_in.email,
            password_hash=hash_password(user_in.password),
            role=user_in.role,
            is_active=True,
        )
        db.add(new_user)
        db.flush()  # to obtain new_user.user_id

        org_name = user_in.organization_name or user_in.name

        # Create role-specific profile
        if user_in.role == "donor":
            donor = Donor(
                user_id=new_user.user_id,
                donor_name=org_name,
                phone=user_in.phone,
                address=user_in.address or "Address not specified",
                latitude=user_in.latitude,
                longitude=user_in.longitude,
            )
            db.add(donor)
        elif user_in.role == "ngo":
            ngo = NGOPartner(
                user_id=new_user.user_id,
                ngo_name=org_name,
                phone=user_in.phone,
                address=user_in.address or "Address not specified",
                latitude=user_in.latitude,
                longitude=user_in.longitude,
            )
            db.add(ngo)
        elif user_in.role == "volunteer":
            volunteer = Volunteer(
                user_id=new_user.user_id,
                volunteer_name=user_in.name,
                phone=user_in.phone,
                availability_status="available",
            )
            db.add(volunteer)

        db.commit()
        db.refresh(new_user)

        access_token = create_access_token(new_user.user_id)
        return Token(
            access_token=access_token,
            token_type="bearer",
            role=new_user.role,
            user_id=new_user.user_id,
            name=new_user.name,
            email=new_user.email,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support.",
        )

    access_token = create_access_token(user.user_id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user_id=user.user_id,
        name=user.name,
        email=user.email,
    )

@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile_data = {}
    if current_user.role == "donor" and current_user.donor:
        profile_data = {
            "donor_id": current_user.donor.donor_id,
            "organization_name": current_user.donor.donor_name,
            "phone": current_user.donor.phone,
            "address": current_user.donor.address,
            "latitude": float(current_user.donor.latitude) if current_user.donor.latitude else None,
            "longitude": float(current_user.donor.longitude) if current_user.donor.longitude else None,
        }
    elif current_user.role == "ngo" and current_user.ngo:
        profile_data = {
            "ngo_id": current_user.ngo.ngo_id,
            "organization_name": current_user.ngo.ngo_name,
            "phone": current_user.ngo.phone,
            "address": current_user.ngo.address,
            "latitude": float(current_user.ngo.latitude) if current_user.ngo.latitude else None,
            "longitude": float(current_user.ngo.longitude) if current_user.ngo.longitude else None,
        }
    elif current_user.role == "volunteer" and current_user.volunteer:
        profile_data = {
            "volunteer_id": current_user.volunteer.volunteer_id,
            "phone": current_user.volunteer.phone,
            "availability_status": current_user.volunteer.availability_status,
        }

    return UserProfileResponse(
        user_id=current_user.user_id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        profile=profile_data,
    )

@router.put("/me", response_model=UserProfileResponse)
def update_my_profile(
    update_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if update_data.name:
        current_user.name = update_data.name

    if current_user.role == "donor" and current_user.donor:
        if update_data.organization_name:
            current_user.donor.donor_name = update_data.organization_name
        if update_data.phone:
            current_user.donor.phone = update_data.phone
        if update_data.address:
            current_user.donor.address = update_data.address
    elif current_user.role == "ngo" and current_user.ngo:
        if update_data.organization_name:
            current_user.ngo.ngo_name = update_data.organization_name
        if update_data.phone:
            current_user.ngo.phone = update_data.phone
        if update_data.address:
            current_user.ngo.address = update_data.address
    elif current_user.role == "volunteer" and current_user.volunteer:
        if update_data.phone:
            current_user.volunteer.phone = update_data.phone
        if update_data.availability_status:
            current_user.volunteer.availability_status = update_data.availability_status

    try:
        db.commit()
        db.refresh(current_user)
        return get_my_profile(current_user, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

