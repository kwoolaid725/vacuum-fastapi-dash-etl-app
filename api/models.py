from .database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Table
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text



test_vacuums = Table('test_vacuums', Base.metadata,
        Column('id', Integer, primary_key=True, nullable=False, index=True),
        Column('test_id', ForeignKey('tests.id')),
        Column('vacuum_inv_no', ForeignKey('vacuums.inv_no'))

 )


class Vacuum(Base):
    __tablename__ = 'vacuums'

    inv_no = Column(Integer, primary_key=True, nullable=False, index=True)
    vac_type_id = Column(Integer, ForeignKey("vac_types.id", ondelete="SET DEFAULT"), server_default='1', nullable=False)
    brand = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    product_stage = Column(String)
    color = Column(String)
    dual_nozzle = Column(Boolean, server_default='False')
    fluffy_nozzle = Column(Boolean, server_default='False')
    self_empty = Column(Boolean, server_default='False')
    self_clean = Column(Boolean, server_default='False')
    release_date = Column(DateTime())
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    image = Column(String)

    tests = relationship("Test", secondary="test_vacuums",back_populates="tested_vacs")
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET DEFAULT"), server_default='9999', nullable=False)

    # CRcordless = relationship("CRcordless", secondary="crcordless_vacuums" ,back_populates="vacuums")
    # CRrobot = relationship("CRrobot", secondary="crrobot_vacuums" ,back_populates="vacuums")
class Test(Base):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    description = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    vac_type_id = Column(Integer, ForeignKey("vac_types.id", ondelete="CASCADE"), nullable=False)
    test_status = Column(String, nullable=False)
    assigned1 = Column(Integer, ForeignKey("users.id", ondelete="SET DEFAULT"), server_default='9999', nullable=False)
    assigned2 = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    last_modified = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    due_date = Column(TIMESTAMP(timezone=True))
    completion_date = Column(TIMESTAMP(timezone=True))
    notes = Column(String)

    tested_vacs = relationship("Vacuum", secondary="test_vacuums",back_populates="tests")
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET DEFAULT"), server_default='9999', nullable=False)

    assigned1_user_rel = relationship("User", foreign_keys="[Test.assigned1]")
    assigned2_user_rel = relationship("User", foreign_keys="[Test.assigned2]")
    owner_user_rel = relationship("User", foreign_keys="[Test.owner_id]")

class TestDetail(Base):
    __tablename__ = 'test_details'

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    test_parent_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    test_category_id = Column(Integer, ForeignKey("test_categories.id", ondelete="CASCADE"), nullable=False)
    vac_type_id = Column(Integer, ForeignKey("vac_types.id", ondelete="CASCADE"), nullable=False)
    test_target_id = Column(Integer, ForeignKey("test_targets.id", ondelete="CASCADE"), nullable=False)
    test_group_id = Column(Integer, ForeignKey("test_groups.id", ondelete="CASCADE"), nullable=False)
    test_measure_id = Column(Integer, ForeignKey("test_measures.id", ondelete="CASCADE"), nullable=False)
    test_case = Column(String)
    tester = Column(Integer, ForeignKey("users.id", ondelete="SET DEFAULT"), server_default='9999', nullable=False)
    inv_no = Column(Integer, ForeignKey("vacuums.inv_no", ondelete="CASCADE"), nullable=False)
    brush_type = Column(String, nullable=False)
    test_measure = Column(String, nullable=False)
    value = Column(String, nullable=False)
    units = Column(String)
    run = Column(Integer, nullable=False)
    run_date = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    notes = Column(String)
    image = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET DEFAULT"), server_default='0', nullable=False)

    vacuum_details = relationship("Vacuum")
    test_details = relationship("Test")


# class CRrobot(Base):
#     __tablename__ = 'cr_robot'
#
#     id = Column(Integer, primary_key=True, nullable=False, index=True)
#     test_parent_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
#
#     cr_robot_test_measure_id = Column(Integer, ForeignKey("cr_robot_test_measure.id", ondelete="CASCADE"), nullable=False)
#     test_case = Column(String)
#     tester = Column(Integer, ForeignKey("users.id", ondelete="SET DEFAULT"), server_default='9999', nullable=False)
#     # vacuum = Column(Integer, ForeignKey("vacuums.inv_no", ondelete="CASCADE"), nullable=False)
#     inv_no = Column(Integer, ForeignKey("vacuums.inv_no", ondelete="CASCADE"), nullable=False)
#     power_setting = Column(String)
#     test_measure = Column(String, nullable=False)
#     value = Column(String, nullable=False)
#     units = Column(String)
#     run = Column(Integer, nullable=False)
#     run_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
#     notes = Column(String)
#     image = Column(String)
#
#     owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET DEFAULT"), server_default='0', nullable=False)
#     vacuum_details = relationship("Vacuum")
#     test_details = relationship("Test")
    # vacuums = relationship("Vacuum", secondary="crcordless_vacuums", back_populates="CRrobot")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class TestCategory(Base):
    __tablename__ = 'test_categories'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    last_modified = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class VacType(Base):
    __tablename__ = 'vac_types'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    last_modified = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class TestTarget(Base):
    __tablename__ = 'test_targets'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    last_modified = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class TestGroup(Base):
    __tablename__ = 'test_groups'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    last_modified = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# class TestTargetGroup(Base):
#     __tablename__ = 'test_target_group'
#     id = Column(Integer, primary_key=True, nullable=False, index=True)
#     test_category_id = Column(Integer, ForeignKey("test_category.id", ondelete="CASCADE"))
#     vac_type_id = Column(Integer, ForeignKey("vac_type.id", ondelete="CASCADE"))
#     test_target = Column(String, nullable=False)
#     test_group = Column(String, nullable=False)
#     last_modified = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class TestMeasure(Base):
    __tablename__ = 'test_measures'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    last_modified = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class CRDI(Base):
    __tablename__ = 'crdi'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    test_measure_id = Column(Integer, ForeignKey("test_measures.id", ondelete="CASCADE"))
    inv_no = Column(Integer, ForeignKey("vacuums.inv_no", ondelete="CASCADE"), nullable=False)
    brand = Column(String)
    model_name = Column(String)
    test_measure = Column(String, nullable=False)
    value = Column(String, nullable=False)
    units = Column(String)
    run = Column(Integer, nullable=False)
    parent_brand = Column(String)
    parent_model = Column(String)
    run_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    last_modified = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET DEFAULT"), server_default='0', nullable=False)
