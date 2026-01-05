from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DataCenterBase(BaseModel):
    dc_name: Optional[str] = None
    coordinates: Optional[str] = None
    date_added: Optional[str] = None


class DataCenterCreate(DataCenterBase):
    id: str


class DataCenterUpdate(DataCenterBase):
    pass


class DataCenter(DataCenterBase):
    id: str

    model_config = {"from_attributes": True}


class DataCenterMetadataBase(BaseModel):
    category: Optional[str] = None
    development_stage: Optional[str] = None
    facility_status: Optional[str] = None
    company_name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    coordinates: Optional[str] = None
    overview: Optional[str] = None
    installed_power_capacity_mw: Optional[float] = None
    installed_area_sq_ft: Optional[float] = None
    tenants: Optional[str] = None
    connectivity_providers: Optional[str] = None
    operation_start_date: Optional[str] = None
    update_date_time: Optional[str] = None
    sources: Optional[str] = None
    num_buildings: Optional[int] = None


class DataCenterMetadataCreate(DataCenterMetadataBase):
    id: str


class DataCenterMetadataUpdate(DataCenterMetadataBase):
    pass


class DataCenterMetadata(DataCenterMetadataBase):
    id: str

    model_config = {"from_attributes": True}


class DataCenterFull(DataCenter):
    """Combined data center with metadata"""
    metadata: Optional[DataCenterMetadata] = None


class DataCenterChangeHistoryBase(BaseModel):
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by_email: str
    changed_by_name: Optional[str] = None
    status: Optional[str] = "approved"


class DataCenterChangeHistoryCreate(DataCenterChangeHistoryBase):
    pass


class DataCenterChangeHistory(DataCenterChangeHistoryBase):
    id: int
    changed_at: datetime

    model_config = {"from_attributes": True}


class UserProfileBase(BaseModel):
    email: str
    username: Optional[str] = None
    company: Optional[str] = None
    date_of_birth: Optional[str] = None
    role: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    company: Optional[str] = None
    date_of_birth: Optional[str] = None
    role: Optional[str] = None


class UserProfile(UserProfileBase):
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

