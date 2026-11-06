"""MPLADS Data Ingestion & Automated ETL Service.

Smart India Hackathon 2026 | Problem Statement ID: 26102
Ministry of Statistics and Programme Implementation (MoSPI)

Handles parsing, schema normalization, entity resolution (Constituencies, Districts,
Agencies), and transactional database upserts for official MPLADS project datasets.
"""

from __future__ import annotations

import csv
import io
import logging
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agency import ImplementingAgency
from app.models.constituency import Constituency
from app.models.district import District
from app.models.milestone import Milestone
from app.models.project import Project
from app.schemas.ingestion import IngestionSummary, ProjectIngestRecord

logger = logging.getLogger("mplad_ai.ingestion")


class MPLADSIngestionService:
    """Core service executing ETL workflows for MPLADS developmental works."""

    @staticmethod
    def parse_csv_stream(csv_file_content: str) -> List[Dict[str, Any]]:
        """Parse raw CSV string into a list of normalized key-value records."""
        reader = csv.DictReader(io.StringIO(csv_file_content.strip()))
        records: List[Dict[str, Any]] = []
        for row in reader:
            cleaned_row = {
                k.strip().lower().replace(" ", "_"): (v.strip() if v else None)
                for k, v in row.items()
                if k
            }
            records.append(cleaned_row)
        return records

    @staticmethod
    async def get_or_create_constituency(
        session: AsyncSession,
        code: str,
        name: str,
        state: str,
        c_type: str = "LOK_SABHA",
        mp_name: Optional[str] = None,
    ) -> Constituency:
        """Fetch existing Constituency or create a new entry."""
        stmt = select(Constituency).where(Constituency.code == code)
        result = await session.execute(stmt)
        instance = result.scalars().first()

        if not instance:
            instance = Constituency(
                id=uuid.uuid4(),
                code=code,
                name=name,
                state=state,
                type=c_type,
                current_mp_name=mp_name,
                annual_entitlement=Decimal("50000000.00"),
            )
            session.add(instance)
            await session.flush()
        return instance

    @staticmethod
    async def get_or_create_district(
        session: AsyncSession,
        name: str,
        state: str,
    ) -> District:
        """Fetch existing District by name and state or create a new entry."""
        stmt = select(District).where(
            District.name.ilike(name.strip()), District.state.ilike(state.strip())
        )
        result = await session.execute(stmt)
        instance = result.scalars().first()

        if not instance:
            instance = District(
                id=uuid.uuid4(),
                name=name.strip(),
                state=state.strip(),
            )
            session.add(instance)
            await session.flush()
        return instance

    @staticmethod
    async def get_or_create_agency(
        session: AsyncSession,
        code: str,
        name: str,
        dept: str,
        district_id: Optional[uuid.UUID] = None,
    ) -> ImplementingAgency:
        """Fetch existing ImplementingAgency or create a new entry."""
        stmt = select(ImplementingAgency).where(ImplementingAgency.code == code)
        result = await session.execute(stmt)
        instance = result.scalars().first()

        if not instance:
            instance = ImplementingAgency(
                id=uuid.uuid4(),
                code=code,
                name=name,
                department=dept or "Rural Development",
                district_id=district_id,
                efficiency_rating=Decimal("3.50"),
            )
            session.add(instance)
            await session.flush()
        return instance

    async def process_batch(
        self,
        session: AsyncSession,
        raw_records: List[Dict[str, Any]],
    ) -> IngestionSummary:
        """Validate, normalize, and upsert a batch of project records into PostgreSQL."""
        batch_id = f"batch-{uuid.uuid4().hex[:8]}"
        inserted_count = 0
        updated_count = 0
        failed_count = 0
        created_constituencies = 0
        created_districts = 0
        created_agencies = 0
        errors: List[Dict[str, Any]] = []

        # Local caches to minimize duplicate SELECT statements
        constituency_cache: Dict[str, uuid.UUID] = {}
        district_cache: Dict[Tuple[str, str], uuid.UUID] = {}
        agency_cache: Dict[str, uuid.UUID] = {}

        for index, raw_item in enumerate(raw_records):
            try:
                # 1. Pydantic validation & normalization
                validated = ProjectIngestRecord(**raw_item)

                # 2. Resolve Constituency
                c_key = validated.constituency_code.upper()
                if c_key in constituency_cache:
                    constituency_id = constituency_cache[c_key]
                else:
                    c_obj = await self.get_or_create_constituency(
                        session=session,
                        code=c_key,
                        name=validated.constituency_name,
                        state=validated.state,
                        c_type=validated.constituency_type,
                        mp_name=validated.mp_name,
                    )
                    constituency_id = c_obj.id
                    constituency_cache[c_key] = constituency_id
                    created_constituencies += 1

                # 3. Resolve District
                d_key = (validated.district_name.lower(), validated.state.lower())
                if d_key in district_cache:
                    district_id = district_cache[d_key]
                else:
                    d_obj = await self.get_or_create_district(
                        session=session,
                        name=validated.district_name,
                        state=validated.state,
                    )
                    district_id = d_obj.id
                    district_cache[d_key] = district_id
                    created_districts += 1

                # 4. Resolve Agency (if specified)
                agency_id = None
                if validated.agency_code and validated.agency_name:
                    a_key = validated.agency_code.upper()
                    if a_key in agency_cache:
                        agency_id = agency_cache[a_key]
                    else:
                        a_obj = await self.get_or_create_agency(
                            session=session,
                            code=a_key,
                            name=validated.agency_name,
                            dept=validated.agency_dept or "Rural Development",
                            district_id=district_id,
                        )
                        agency_id = a_obj.id
                        agency_cache[a_key] = agency_id
                        created_agencies += 1

                # 5. Check if project already exists (upsert)
                stmt = select(Project).where(Project.project_code == validated.project_code)
                res = await session.execute(stmt)
                existing_project = res.scalars().first()

                if existing_project:
                    # Update fields
                    existing_project.title = validated.title
                    existing_project.description = validated.description
                    existing_project.category = validated.category
                    existing_project.priority_quota = validated.priority_quota
                    existing_project.estimated_cost = validated.estimated_cost
                    existing_project.sanctioned_cost = validated.sanctioned_cost
                    existing_project.actual_expenditure = validated.actual_expenditure
                    existing_project.status = validated.status
                    existing_project.latitude = validated.latitude
                    existing_project.longitude = validated.longitude
                    existing_project.location_address = validated.location_address
                    existing_project.sanction_date = validated.sanction_date
                    existing_project.work_order_date = validated.work_order_date
                    existing_project.target_completion_date = validated.target_completion_date
                    existing_project.actual_completion_date = validated.actual_completion_date
                    if agency_id:
                        existing_project.agency_id = agency_id
                    updated_count += 1
                else:
                    # Create new project
                    new_proj_id = uuid.uuid4()
                    new_project = Project(
                        id=new_proj_id,
                        project_code=validated.project_code,
                        constituency_id=constituency_id,
                        district_id=district_id,
                        agency_id=agency_id,
                        title=validated.title,
                        description=validated.description,
                        category=validated.category,
                        priority_quota=validated.priority_quota,
                        estimated_cost=validated.estimated_cost,
                        sanctioned_cost=validated.sanctioned_cost,
                        actual_expenditure=validated.actual_expenditure,
                        status=validated.status,
                        latitude=validated.latitude,
                        longitude=validated.longitude,
                        location_address=validated.location_address,
                        recommendation_date=validated.recommendation_date,
                        sanction_date=validated.sanction_date,
                        work_order_date=validated.work_order_date,
                        target_completion_date=validated.target_completion_date,
                        actual_completion_date=validated.actual_completion_date,
                    )
                    session.add(new_project)

                    # Initialize default milestone sequence
                    self._create_default_milestones(session, new_proj_id, validated)
                    inserted_count += 1

            except Exception as exc:
                failed_count += 1
                error_msg = str(exc)
                logger.warning("Failed to ingest row %d: %s", index, error_msg)
                errors.append({"row_index": index, "raw": raw_item, "error": error_msg})

        await session.flush()

        return IngestionSummary(
            status="success" if failed_count == 0 else "partial_success",
            batch_id=batch_id,
            total_records=len(raw_records),
            inserted_records=inserted_count,
            updated_records=updated_count,
            failed_records=failed_count,
            constituencies_created=created_constituencies,
            districts_created=created_districts,
            agencies_created=created_agencies,
            errors=errors,
        )

    @staticmethod
    def _create_default_milestones(
        session: AsyncSession, project_id: uuid.UUID, record: ProjectIngestRecord
    ) -> None:
        """Create foundational 4-stage milestones for tracking physical progress."""
        stages = [
            ("Stage 1: Administrative Approval & Site Verification", 1, 10),
            ("Stage 2: Technical Sanction & Tendering", 2, 25),
            ("Stage 3: Physical Work Execution", 3, 50),
            ("Stage 4: Completion & Utilization Certificate Issued", 4, 15),
        ]

        # Calculate milestone target dates based on recommendation & completion target
        total_days = max(30, (record.target_completion_date - record.recommendation_date).days)
        step_days = total_days // 4

        for name, seq, weight in stages:
            m_date = record.recommendation_date + timedelta(days=step_days * seq)
            milestone = Milestone(
                id=uuid.uuid4(),
                project_id=project_id,
                name=name,
                sequence_order=seq,
                weight_percentage=Decimal(str(weight)),
                status="COMPLETED" if record.status == "COMPLETED" else "PENDING",
                target_date=m_date,
            )
            session.add(milestone)

    @staticmethod
    def get_seed_dataset() -> List[Dict[str, Any]]:
        """Returns realistic, high-fidelity sample MPLADS developmental projects."""
        return [
            {
                "project_code": "MPLADS-2024-UP-001",
                "title": "Solar Powered RO Drinking Water Plants in Rural Hamlets",
                "description": "Installation of 10 community solar RO water purification plants in flood-prone villages",
                "category": "DRINKING_WATER",
                "priority_quota": "SC_MANDATE",
                "state": "Uttar Pradesh",
                "constituency_code": "PC-UP-77",
                "constituency_name": "Varanasi",
                "constituency_type": "LOK_SABHA",
                "mp_name": "Narendra Modi",
                "district_name": "Varanasi",
                "agency_code": "UP-JAL-NIGAM",
                "agency_name": "UP Jal Nigam Rural Division",
                "agency_dept": "Public Health Engineering",
                "estimated_cost": "4500000.00",
                "sanctioned_cost": "4250000.00",
                "actual_expenditure": "2100000.00",
                "status": "IN_PROGRESS",
                "latitude": "25.3176000",
                "longitude": "82.9739000",
                "location_address": "Rohania Block, Varanasi District",
                "recommendation_date": "2024-01-15",
                "sanction_date": "2024-02-10",
                "work_order_date": "2024-03-01",
                "target_completion_date": "2024-11-30",
            },
            {
                "project_code": "MPLADS-2024-KL-002",
                "title": "Smart Digital Classrooms & STEM Labs in Government High Schools",
                "description": "Modernization of 15 tribal community schools with interactive smart boards and computers",
                "category": "EDUCATION",
                "priority_quota": "ST_MANDATE",
                "state": "Kerala",
                "constituency_code": "PC-KL-04",
                "constituency_name": "Wayanad",
                "constituency_type": "LOK_SABHA",
                "mp_name": "Priyanka Gandhi Vadra",
                "district_name": "Wayanad",
                "agency_code": "KERALA-KITE",
                "agency_name": "Kerala Infrastructure and Technology for Education",
                "agency_dept": "General Education",
                "estimated_cost": "3800000.00",
                "sanctioned_cost": "3800000.00",
                "actual_expenditure": "3800000.00",
                "status": "COMPLETED",
                "latitude": "11.6854000",
                "longitude": "76.1320000",
                "location_address": "Sulthan Bathery, Wayanad",
                "recommendation_date": "2023-08-20",
                "sanction_date": "2023-09-15",
                "work_order_date": "2023-10-01",
                "target_completion_date": "2024-04-30",
                "actual_completion_date": "2024-04-15",
            },
            {
                "project_code": "MPLADS-2024-DL-003",
                "title": "Community Health Center Oxygen Generation & Critical Diagnostic Wing",
                "description": "Establishment of automated PSA oxygen generation plant and digital radiography unit",
                "category": "PUBLIC_HEALTH",
                "priority_quota": "GENERAL",
                "state": "Delhi",
                "constituency_code": "PC-DL-04",
                "constituency_name": "New Delhi",
                "constituency_type": "LOK_SABHA",
                "mp_name": "Bansuri Swaraj",
                "district_name": "New Delhi",
                "agency_code": "CPWD-DELHI-01",
                "agency_name": "Central Public Works Department",
                "agency_dept": "Health Infrastructure",
                "estimated_cost": "7200000.00",
                "sanctioned_cost": "6900000.00",
                "actual_expenditure": "1200000.00",
                "status": "IN_PROGRESS",
                "latitude": "28.6139000",
                "longitude": "77.2090000",
                "location_address": "Charak Palika Hospital Complex, Moti Bagh",
                "recommendation_date": "2024-02-01",
                "sanction_date": "2024-03-05",
                "work_order_date": "2024-03-20",
                "target_completion_date": "2024-12-31",
            },
            {
                "project_code": "MPLADS-2024-KA-004",
                "title": "All-Weather Concrete Link Road & Drainage Network",
                "description": "Construction of 3.2 km all-weather cement concrete road connecting peri-urban hamlets",
                "category": "ROADS_BRIDGES",
                "priority_quota": "GENERAL",
                "state": "Karnataka",
                "constituency_code": "PC-KA-26",
                "constituency_name": "Bangalore South",
                "constituency_type": "LOK_SABHA",
                "mp_name": "Tejasvi Surya",
                "district_name": "Bengaluru Urban",
                "agency_code": "BBMP-ENGG-02",
                "agency_name": "Bruhat Bengaluru Mahanagara Palike",
                "agency_dept": "Urban Road Works",
                "estimated_cost": "9500000.00",
                "sanctioned_cost": "9200000.00",
                "actual_expenditure": "8800000.00",
                "status": "STALLED",  # Anomaly candidate: high expenditure but stalled
                "latitude": "12.9250000",
                "longitude": "77.5898000",
                "location_address": "Konanakunte Cross Road, Bengaluru South",
                "recommendation_date": "2023-05-10",
                "sanction_date": "2023-06-12",
                "work_order_date": "2023-07-01",
                "target_completion_date": "2024-01-15",
            },
            {
                "project_code": "MPLADS-2024-MH-005",
                "title": "Solar Powered Drip Irrigation & Community Check Dam Revitalization",
                "description": "Deepening and rejuvenation of 4 percolation tanks with automated solar distribution pumps",
                "category": "IRRIGATION",
                "priority_quota": "GENERAL",
                "state": "Maharashtra",
                "constituency_code": "PC-MH-35",
                "constituency_name": "Baramati",
                "constituency_type": "LOK_SABHA",
                "mp_name": "Supriya Sule",
                "district_name": "Pune",
                "agency_code": "MHA-ZP-PUNE",
                "agency_name": "Zilla Parishad Pune Minor Irrigation",
                "agency_dept": "Water Conservation",
                "estimated_cost": "5500000.00",
                "sanctioned_cost": "5400000.00",
                "actual_expenditure": "2700000.00",
                "status": "IN_PROGRESS",
                "latitude": "18.1517000",
                "longitude": "74.5770000",
                "location_address": "Daund-Baramati Border Canal Sector",
                "recommendation_date": "2024-03-01",
                "sanction_date": "2024-04-10",
                "work_order_date": "2024-04-25",
                "target_completion_date": "2025-01-30",
            },
        ]
