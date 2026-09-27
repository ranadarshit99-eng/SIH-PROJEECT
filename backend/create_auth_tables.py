import hashlib
import uuid
import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from database import engine

def hash_password(password: str) -> str:
    """Enterprise password hashing using SHA-256 with salt."""
    salt = "SIH_ENTERPRISE_SECURE_SALT_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def init_auth_tables():
    """Ensure all required auth, session, tender and submission tables exist with proper schemas."""
    with engine.begin() as conn:
        # Create system_users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS system_users (
                id VARCHAR(64) PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                user_type VARCHAR(20) NOT NULL,
                full_name VARCHAR(255),
                organization VARCHAR(255),
                designation VARCHAR(100),
                gstin VARCHAR(50),
                department VARCHAR(100),
                created_at VARCHAR(50)
            );
        """))
        
        # Create auth_sessions table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS auth_sessions (
                session_id VARCHAR(128) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                user_type VARCHAR(20) NOT NULL,
                email VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                organization VARCHAR(255),
                ip_address VARCHAR(45),
                user_agent TEXT,
                is_active INTEGER DEFAULT 1,
                created_at VARCHAR(50),
                expires_at VARCHAR(50),
                last_accessed_at VARCHAR(50),
                session_metadata TEXT
            );
        """))

        # Create tender_submissions table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tender_submissions (
                id VARCHAR(128) PRIMARY KEY,
                tender_id VARCHAR(128) NOT NULL,
                user_id VARCHAR(64) NOT NULL,
                bidder_name VARCHAR(255),
                bidder_email VARCHAR(255),
                bidder_gstin VARCHAR(100),
                bidder_org VARCHAR(255),
                bidder_designation VARCHAR(100),
                form_data TEXT,
                evaluation_output TEXT,
                files_map TEXT,
                submitted_at VARCHAR(50),
                status VARCHAR(50) DEFAULT 'SUBMITTED'
            );
        """))

        # Create bis_details table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS bis_details (
                id VARCHAR(64) PRIMARY KEY,
                cml_no VARCHAR(100),
                cml_licence_no VARCHAR(100),
                licence_holder VARCHAR(255),
                licensee_name VARCHAR(255),
                factory_address TEXT,
                product VARCHAR(255),
                indian_standard_no VARCHAR(100),
                endorsement_no VARCHAR(100),
                endorsement_date VARCHAR(50),
                licence_validity VARCHAR(50),
                authorized_signatory VARCHAR(255),
                branch_office VARCHAR(255)
            );
        """))

        # Create msme_details table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS msme_details (
                id VARCHAR(64) PRIMARY KEY,
                udyam_registration_no VARCHAR(100),
                registration_no VARCHAR(100),
                enterprise_name VARCHAR(255),
                enterprise_type VARCHAR(100),
                organisation_type VARCHAR(100),
                date_of_incorporation VARCHAR(50),
                official_address TEXT,
                nic_2_digit VARCHAR(50),
                nic_4_digit VARCHAR(50),
                business_activity VARCHAR(255)
            );
        """))

        # Create gst_details table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS gst_details (
                id VARCHAR(64) PRIMARY KEY,
                gstin_registration_no VARCHAR(100),
                legal_name VARCHAR(255),
                trade_name VARCHAR(255),
                constitution_of_business VARCHAR(100),
                principal_business_address TEXT,
                type_of_registration VARCHAR(100),
                date_of_issue VARCHAR(50),
                approving_authority VARCHAR(255),
                jurisdictional_office VARCHAR(255)
            );
        """))

        # Create pan_details table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pan_details (
                id VARCHAR(64) PRIMARY KEY,
                pan_no VARCHAR(50),
                person_name VARCHAR(255),
                birth_date VARCHAR(50)
            );
        """))

        # Create iso_details table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS iso_details (
                id VARCHAR(64) PRIMARY KEY,
                certificate_no VARCHAR(100),
                certificate_holder VARCHAR(255),
                company_name VARCHAR(255),
                authorized_person VARCHAR(255),
                scope_of_certification VARCHAR(255),
                registered_address TEXT,
                issue_date VARCHAR(50),
                valid_until VARCHAR(50)
            );
        """))

        # Create financial_statement_details table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS financial_statement_details (
                id VARCHAR(64) PRIMARY KEY,
                document_reference VARCHAR(100),
                authorized_person VARCHAR(255),
                enterprise_bidder VARCHAR(255),
                financial_year VARCHAR(50),
                revenue_turnover VARCHAR(100),
                demo_record_no VARCHAR(50)
            );
        """))

        # Create experience_details table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS experience_details (
                id VARCHAR(64) PRIMARY KEY,
                document_reference VARCHAR(100),
                authorized_person VARCHAR(255),
                enterprise_bidder VARCHAR(255),
                project_work TEXT,
                client_reference VARCHAR(255),
                contract_value VARCHAR(100),
                completion_period VARCHAR(100),
                demo_record_no VARCHAR(50)
            );
        """))

        # Create work_completion_details table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS work_completion_details (
                id VARCHAR(64) PRIMARY KEY,
                document_reference VARCHAR(100),
                work_order_no VARCHAR(100),
                authorized_person VARCHAR(255),
                enterprise_company_name VARCHAR(255),
                work_description TEXT,
                contract_value VARCHAR(100),
                completion_date VARCHAR(50),
                demo_record_no VARCHAR(50)
            );
        """))

        # Create turnover_details table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS turnover_details (
                id VARCHAR(64) PRIMARY KEY,
                authorized_person VARCHAR(255),
                enterprise_company_name VARCHAR(255),
                turnover_amount VARCHAR(100),
                average_turnover VARCHAR(100),
                authorized_signatory VARCHAR(255),
                created_at VARCHAR(50)
            );
        """))

        # Create annexure_m table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS annexure_m (
                id VARCHAR(64) PRIMARY KEY,
                company_bidder_name VARCHAR(255),
                tender_no VARCHAR(100),
                required_local_content_percent VARCHAR(50),
                declared_local_content_percent VARCHAR(50),
                local_value_addition_location TEXT,
                compliance_result VARCHAR(100),
                authorized_signatory VARCHAR(255)
            );
        """))

        # Create itr_details table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS itr_details (
                id VARCHAR(64) PRIMARY KEY,
                ack_number VARCHAR(100),
                taxpayer_name VARCHAR(255),
                pan_number VARCHAR(50),
                assessment_year VARCHAR(50),
                address TEXT
            );
        """))

        # Seed bis_details if empty
        b_cnt = conn.execute(text("SELECT COUNT(*) FROM bis_details")).scalar()
        if b_cnt == 0:
            conn.execute(text("""
                INSERT INTO bis_details 
                (id, cml_no, cml_licence_no, licence_holder, licensee_name, factory_address, product, indian_standard_no, endorsement_no, endorsement_date, licence_validity, authorized_signatory, branch_office)
                VALUES ('bis_1', 'CM/L-4561000822', 'CM/L-4561000822', 'SHAH INDUSTRIAL EQUIPMENTS', 'SHAH INDUSTRIAL EQUIPMENTS', 'Naroda GIDC, Ahmedabad, Gujarat', 'Industrial machinery and equipment manufacturing', 'IS DEMO 2819 : 2026', '21', '29-Aug-2026', '30-Jun-2027', 'Yash Shah', 'Mumbai Branch Office-I');
            """))
            conn.execute(text("""
                INSERT INTO bis_details 
                (id, cml_no, cml_licence_no, licence_holder, licensee_name, factory_address, product, indian_standard_no, endorsement_no, endorsement_date, licence_validity, authorized_signatory, branch_office)
                VALUES ('bis_2', 'CML-8742910', 'CML-8742910', 'Tata Infrastructure Pvt Ltd', 'Tata Infrastructure Pvt Ltd', 'Plot 42, Commercial Hub, Sector 18, Mumbai - 400051', 'Prestressed Concrete Wires & Cables', 'IS 14268:2022', 'END-2024-098', '2020-06-12', '2027-12-31', 'Tata Infrastructure Pvt Ltd', 'Mumbai Division');
            """))

        # Seed msme_details if empty
        m_cnt = conn.execute(text("SELECT COUNT(*) FROM msme_details")).scalar()
        if m_cnt == 0:
            conn.execute(text("""
                INSERT INTO msme_details 
                (id, udyam_registration_no, registration_no, enterprise_name, enterprise_type, organisation_type, date_of_incorporation, official_address, nic_2_digit, nic_4_digit, business_activity)
                VALUES ('msme_1', 'GJ-24-1234506', 'GJ-24-1234506', 'SHAH INDUSTRIAL EQUIPMENTS', 'Micro', 'Private Limited Company', '16-08-2015', 'Naroda GIDC, Ahmedabad, Gujarat', '28', '2819', 'Industrial machinery and equipment manufacturing');
            """))
            conn.execute(text("""
                INSERT INTO msme_details 
                (id, udyam_registration_no, registration_no, enterprise_name, enterprise_type, organisation_type, date_of_incorporation, official_address, nic_2_digit, nic_4_digit, business_activity)
                VALUES ('msme_2', 'UDYAM-MH-03-0098412', 'UDYAM-MH-03-0098412', 'Tata Infrastructure Pvt Ltd', 'Medium', 'Private Limited Company', '2010-04-15', 'Plot 42, Commercial Hub, Sector 18, Mumbai - 400051', '42', '4210', 'Construction of utility projects');
            """))

        # Seed gst_details if empty
        g_cnt = conn.execute(text("SELECT COUNT(*) FROM gst_details")).scalar()
        if g_cnt == 0:
            conn.execute(text("""
                INSERT INTO gst_details 
                (id, gstin_registration_no, legal_name, trade_name, constitution_of_business, principal_business_address, type_of_registration, date_of_issue, approving_authority, jurisdictional_office)
                VALUES ('gst_1', '27AAAAA0000A1Z5', 'Tata Infrastructure Pvt Ltd', 'Tata Infrastructure', 'Private Limited Company', 'Plot 42, Commercial Hub, Sector 18, Mumbai - 400051', 'Regular Taxpayer', '2020-06-12', 'Assistant Commissioner of GST', 'WZR-04 Mumbai Division');
            """))

        # Seed pan_details if empty
        p_cnt = conn.execute(text("SELECT COUNT(*) FROM pan_details")).scalar()
        if p_cnt == 0:
            conn.execute(text("""
                INSERT INTO pan_details 
                (id, pan_no, person_name, birth_date)
                VALUES ('pan_1', 'AAAAA0000A', 'Tata Infrastructure Pvt Ltd', '1992-04-18');
            """))

        # Seed iso_details if empty
        i_cnt = conn.execute(text("SELECT COUNT(*) FROM iso_details")).scalar()
        if i_cnt == 0:
            conn.execute(text("""
                INSERT INTO iso_details 
                (id, certificate_no, certificate_holder, company_name, authorized_person, scope_of_certification, registered_address, issue_date, valid_until)
                VALUES ('iso_1', 'ISO-9001-8842', 'SHAH INDUSTRIAL EQUIPMENTS', 'SHAH INDUSTRIAL EQUIPMENTS', 'Yash Shah', 'Quality Management System - Manufacturing & Supply', 'Naroda GIDC, Ahmedabad, Gujarat', '2022-01-15', '2028-01-14');
            """))
            conn.execute(text("""
                INSERT INTO iso_details 
                (id, certificate_no, certificate_holder, company_name, authorized_person, scope_of_certification, registered_address, issue_date, valid_until)
                VALUES ('iso_2', 'ISO-9001-9901', 'Tata Infrastructure Pvt Ltd', 'Tata Infrastructure Pvt Ltd', 'Rajesh Sharma', 'Infrastructure Engineering & Construction', 'Plot 42, Commercial Hub, Sector 18, Mumbai - 400051', '2021-05-10', '2027-05-09');
            """))

        # Seed financial_statement_details if empty
        fin_cnt = conn.execute(text("SELECT COUNT(*) FROM financial_statement_details")).scalar()
        if fin_cnt == 0:
            conn.execute(text("""
                INSERT INTO financial_statement_details 
                (id, document_reference, authorized_person, enterprise_bidder, financial_year, revenue_turnover, demo_record_no)
                VALUES ('fin_1', 'FIN-2026-901', 'Yash Shah', 'SHAH INDUSTRIAL EQUIPMENTS', '2025-2026', '₹15.4 Crores', 'DEMO-FIN-01');
            """))
            conn.execute(text("""
                INSERT INTO financial_statement_details 
                (id, document_reference, authorized_person, enterprise_bidder, financial_year, revenue_turnover, demo_record_no)
                VALUES ('fin_2', 'FIN-2026-902', 'Rajesh Sharma', 'Tata Infrastructure Pvt Ltd', '2025-2026', '₹450 Crores', 'DEMO-FIN-02');
            """))

        # Create government_tenders table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS government_tenders (
                id VARCHAR(128) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                department VARCHAR(255),
                budget VARCHAR(100),
                deadline VARCHAR(50),
                created_by_officer_id VARCHAR(64),
                created_by_officer_name VARCHAR(255),
                fields_schema TEXT,
                created_at VARCHAR(50)
            );
        """))

        # Seed initial tenders if table is empty
        t_res = conn.execute(text("SELECT COUNT(*) FROM government_tenders")).scalar()
        if t_res == 0:
            now_str = datetime.now(timezone.utc).isoformat()
            
            fields_t1 = [
                {"id": "f_1", "label": "Company Registration Name", "type": "text", "required": True},
                {"id": "f_2", "label": "Quotation Amount (INR)", "type": "text", "required": True},
                {"id": "doc_gst", "label": "GST Certificate", "type": "file", "docType": "gst", "required": True},
                {"id": "doc_pan", "label": "PAN Card", "type": "file", "docType": "pan", "required": True},
                {"id": "doc_iso", "label": "ISO Certificate", "type": "file", "docType": "iso", "required": False},
                {"id": "doc_financial", "label": "Financial Statement", "type": "file", "docType": "financial", "required": True}
            ]
            conn.execute(
                text("""
                    INSERT INTO government_tenders 
                    (id, title, description, department, budget, deadline, created_by_officer_id, created_by_officer_name, fields_schema, created_at)
                    VALUES (:id, :title, :description, :department, :budget, :deadline, :created_by_officer_id, :created_by_officer_name, :fields_schema, :created_at)
                """),
                {
                    "id": "t_101",
                    "title": "National Highway Expansion Project Phase-4",
                    "description": "Procurement of civil construction services for 120km highway expansion including bridge construction and toll plaza automation.",
                    "department": "Ministry of Road Transport & Highways",
                    "budget": "₹450 Crores",
                    "deadline": "2026-10-30",
                    "created_by_officer_id": "usr_officer_admin",
                    "created_by_officer_name": "Dr. Rajesh Kumar Varma",
                    "fields_schema": json.dumps(fields_t1),
                    "created_at": now_str
                }
            )

            fields_t2 = [
                {"id": "f_1", "label": "Vendor Name", "type": "text", "required": True},
                {"id": "doc_gst", "label": "GST Certificate", "type": "file", "docType": "gst", "required": True},
                {"id": "doc_msme", "label": "MSME Certificate", "type": "file", "docType": "msme", "required": True},
                {"id": "doc_oem", "label": "OEM Authorization", "type": "file", "docType": "oem", "required": True},
                {"id": "doc_turnover", "label": "Turnover Certificate", "type": "file", "docType": "turnover", "required": True}
            ]
            conn.execute(
                text("""
                    INSERT INTO government_tenders 
                    (id, title, description, department, budget, deadline, created_by_officer_id, created_by_officer_name, fields_schema, created_at)
                    VALUES (:id, :title, :description, :department, :budget, :deadline, :created_by_officer_id, :created_by_officer_name, :fields_schema, :created_at)
                """),
                {
                    "id": "t_102",
                    "title": "Smart City Solar Grid Installation",
                    "description": "Supply, installation and maintenance of 50MW rooftop solar infrastructure across municipal buildings.",
                    "department": "Ministry of New & Renewable Energy",
                    "budget": "₹85 Crores",
                    "deadline": "2026-11-15",
                    "created_by_officer_id": "usr_officer_admin",
                    "created_by_officer_name": "Dr. Rajesh Kumar Varma",
                    "fields_schema": json.dumps(fields_t2),
                    "created_at": now_str
                }
            )

        # Seed initial official accounts if table is empty
        res = conn.execute(text("SELECT COUNT(*) FROM system_users")).scalar()
        if res == 0:
            now_str = datetime.now(timezone.utc).isoformat()
            
            # Seed 1: Official Government Officer
            officer_id = "usr_officer_admin"
            conn.execute(
                text("""
                    INSERT INTO system_users 
                    (id, username, email, password_hash, user_type, full_name, organization, designation, department, created_at)
                    VALUES (:id, :username, :email, :password_hash, :user_type, :full_name, :organization, :designation, :department, :created_at)
                """),
                {
                    "id": officer_id,
                    "username": "officer_admin",
                    "email": "officer@gov.in",
                    "password_hash": hash_password("Officer@123"),
                    "user_type": "officer",
                    "full_name": "Dr. Rajesh Kumar Varma",
                    "organization": "Ministry of Road Transport & Highways",
                    "designation": "Chief Procurement Officer & Auditor",
                    "department": "National Infrastructure Authority",
                    "created_at": now_str
                }
            )

            # Seed 2: Official Verified Bidder (Tata Infrastructure)
            bidder1_id = "usr_bidder_tata"
            conn.execute(
                text("""
                    INSERT INTO system_users 
                    (id, username, email, password_hash, user_type, full_name, organization, gstin, created_at)
                    VALUES (:id, :username, :email, :password_hash, :user_type, :full_name, :organization, :gstin, :created_at)
                """),
                {
                    "id": bidder1_id,
                    "username": "tata_infra",
                    "email": "bids@tatainfra.com",
                    "password_hash": hash_password("Bidder@123"),
                    "user_type": "bidder",
                    "full_name": "Tata Infrastructure Pvt Ltd",
                    "organization": "Tata Group Infrastructure Div",
                    "gstin": "27AAAAA0000A1Z5",
                    "created_at": now_str
                }
            )

    print("[Database] Auth tables initialized successfully!")

if __name__ == "__main__":
    init_auth_tables()

