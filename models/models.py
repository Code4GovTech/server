from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float,BigInteger, Boolean, SmallInteger, func, ForeignKey,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, DateTime as SA_DateTime
from datetime import datetime


Base = declarative_base()

class DateTime(TypeDecorator):
    impl = SA_DateTime

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            try:
                # Convert string to datetime
                return datetime.fromisoformat(value)
            except ValueError:
                # If conversion fails, return None
                return None
        return value

    def process_result_value(self, value, dialect):
        return value


class AppComments(Base):
    __tablename__ = 'app_comments'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    updated_at = Column(DateTime, nullable=True)
    api_url = Column(Text, nullable=True)
    comment_id = Column(BigInteger, nullable=True)
    issue_id = Column(BigInteger, unique=True)

    def __repr__(self):
        return f"<AppComments(id={self.id})>"

    def to_dict(self):
        return {
            'id': str(self.id),
            'updated_at': self.updated_at,
            'api_url': self.api_url,
            'comment_id': self.comment_id,
            'issue_id': self.issue_id
        }

class Badges(Base):
    __tablename__ = 'badges'
    id = Column(UUID(as_uuid=True), primary_key=True)
    image = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    user_badges = relationship('UserBadges', back_populates='badge')


    def __repr__(self):
        return f"<Badges(image={self.image})>"

    def to_dict(self):
        return {
            'image': self.image,
            'text': self.text,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class CcbpTickets(Base):
    __tablename__ = 'ccbp_tickets'
    __table_args__ = {'comment': 'A table to store details of CCBP Tickets from various projects'}

    created_at = Column(DateTime, nullable=True)
    name = Column(Text, nullable=True)
    product = Column(Text, nullable=True)
    complexity = Column(Text, nullable=True)
    project_category = Column(Text, nullable=True)
    project_sub_category = Column(Text, nullable=True)
    reqd_skills = Column(Text, nullable=True)
    issue_id = Column(BigInteger, unique=True)
    api_endpoint_url = Column(Text, unique=True, nullable=True)
    url = Column(Text, unique=True, nullable=True)
    ticket_points = Column(SmallInteger, nullable=True, comment='How many points the ticket is worth')
    index = Column(SmallInteger, unique=True, autoincrement=True)
    mentors = Column(Text, nullable=True)
    uuid = Column(UUID(as_uuid=True), primary_key=True)
    status = Column(Text, nullable=True)
    community_label = Column(Boolean, nullable=True, comment='has community label')
    organization = Column(Text, nullable=True)
    closed_at = Column(DateTime, nullable=True, comment='date-time at which issue was closed')
    assignees = Column(Text, nullable=True)
    issue_author = Column(Text, nullable=True)
    is_assigned = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<CcbpTickets(uuid={self.uuid})>"

    def to_dict(self):
        return {
            'created_at': self.created_at,
            'name': self.name,
            'product': self.product,
            'complexity': self.complexity,
            'project_category': self.project_category,
            'project_sub_category': self.project_sub_category,
            'reqd_skills': self.reqd_skills,
            'issue_id': self.issue_id,
            'api_endpoint_url': self.api_endpoint_url,
            'url': self.url,
            'ticket_points': self.ticket_points,
            'index': self.index,
            'mentors': self.mentors,
            'uuid': str(self.uuid),
            'status': self.status,
            'community_label': self.community_label,
            'organization': self.organization,
            'closed_at': self.closed_at,
            'assignees': self.assignees,
            'issue_author': self.issue_author,
            'is_assigned': self.is_assigned
        }

class Chapters(Base):
    __tablename__ = 'chapters'
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    type = Column(Text, nullable=True)
    org_name = Column(Text, unique=True)
    primary_organisation = Column(Text, nullable=True, comment='the organisation that the chapter is mapped to')
    sessions = Column(Integer, nullable=True)
    discord_role_id = Column(BigInteger, unique=True, comment='db id of the corresponding member role in discord server')
    created_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Chapters(id={self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'org_name': self.org_name,
            'primary_organisation': self.primary_organisation,
            'sessions': self.sessions,
            'discord_role_id': self.discord_role_id,
            'created_at': self.created_at
        }


##

class ConnectedPrs(Base):
    __tablename__ = 'connected_prs'

    id = Column(UUID(as_uuid=True), primary_key=True)
    created_at = Column(DateTime, nullable=True)
    api_url = Column(Text, nullable=True)
    html_url = Column(Text, unique=True, nullable=True)
    raised_by = Column(BigInteger, nullable=True)
    raised_at = Column(DateTime, nullable=False)
    raised_by_username = Column(Text, nullable=False)
    status = Column(Text, nullable=True)
    is_merged = Column(Boolean, nullable=True)
    merged_by = Column(BigInteger, nullable=True)
    merged_at = Column(Text, nullable=True)
    merged_by_username = Column(Text, nullable=True)
    pr_id = Column(BigInteger, nullable=False, comment='github id of the pr')
    points = Column(SmallInteger, nullable=False)
    ticket_url = Column(Text, nullable=False)
    ticket_complexity = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ConnectedPrs(id={self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'api_url': self.api_url,
            'html_url': self.html_url,
            'raised_by': self.raised_by,
            'raised_at': self.raised_at,
            'raised_by_username': self.raised_by_username,
            'status': self.status,
            'is_merged': self.is_merged,
            'merged_by': self.merged_by,
            'merged_at': self.merged_at,
            'merged_by_username': self.merged_by_username,
            'pr_id': self.pr_id,
            'points': self.points,
            'ticket_url': self.ticket_url,
            'ticket_complexity': self.ticket_complexity
        }

class ContributorNames(Base):
    __tablename__ = 'contributor_names'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    discord_id = Column(BigInteger, nullable=False)
    name = Column(Text, nullable=True)
    country = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ContributorNames(id={self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'discord_id': self.discord_id,
            'name': self.name,
            'country': self.country
        }

class ContributorsDiscord(Base):
    __tablename__ = 'contributors_discord'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    discord_id = Column(BigInteger, unique=True, nullable=False)
    github_id = Column(BigInteger, nullable=True)
    github_url = Column(String, nullable=True)
    discord_username = Column(String, nullable=True)
    joined_at = Column(DateTime, nullable=False)
    email = Column(Text, nullable=True)
    field_name = Column(Text, nullable=True, name='name')  # Adjusted field name
    chapter = Column(Text, nullable=True, comment="the chapter they're associated with")
    gender = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<ContributorsDiscord(id={self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'discord_id': self.discord_id,
            'github_id': self.github_id,
            'github_url': self.github_url,
            'discord_username': self.discord_username,
            'joined_at': self.joined_at,
            'email': self.email,
            'name': self.field_name,
            'chapter': self.chapter,
            'gender': self.gender,
            'is_active': self.is_active
        }
        
class ContributorsRegistration(Base):
    __tablename__ = 'contributors_registration'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    discord_id = Column(BigInteger, unique=True, nullable=False)
    github_id = Column(BigInteger, unique=True, nullable=False)
    github_url = Column(String, nullable=False)
    discord_username = Column(String, nullable=True)
    joined_at = Column(DateTime, nullable=False)
    email = Column(Text, nullable=True)
    name = Column(Text, nullable=True)
    
    point_transactions = relationship('PointTransactions', back_populates='contributor')
    
    user_activities = relationship('UserActivity', back_populates='contributor')
    user_points_mappings = relationship('UserPointsMapping', back_populates='contributors')


    def __repr__(self):
        return f"<ContributorsRegistration(id={self.id})>"


    def to_dict(self):
        return {
            'id': self.id,
            'discord_id': self.discord_id,
            'github_id': self.github_id,
            'github_url': self.github_url,
            'discord_username': self.discord_username,
            'joined_at': self.joined_at,
            'email': self.email,
            'name': self.name
        }

class DiscordChannels(Base):
    __tablename__ = 'discord_channels'

    channel_id = Column(BigInteger, primary_key=True)
    channel_name = Column(Text, nullable=True)
    webhook = Column(Text, nullable=True)
    should_notify = Column(Boolean, nullable=False)
    
    products = relationship('Product', back_populates='channel')


    def __repr__(self):
        return f"<DiscordChannels(channel_id={self.channel_id})>"

    def to_dict(self):
        return {
            'channel_id': self.channel_id,
            'channel_name': self.channel_name,
            'webhook': self.webhook,
            'should_notify': self.should_notify
        }

class DiscordEngagement(Base):
    __tablename__ = 'discord_engagement'
    __table_args__ = {'comment': 'engagement metrics for contributors'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=True)
    contributor = Column(BigInteger, unique=True, nullable=False)
    has_introduced = Column(Boolean, nullable=True)
    total_message_count = Column(BigInteger, nullable=True)
    total_reaction_count = Column(BigInteger, nullable=True)
    converserbadge = Column(Boolean, nullable=True)
    apprenticebadge = Column(Boolean, nullable=True)
    rockstarbadge = Column(Boolean, nullable=True)
    enthusiastbadge = Column(Boolean, nullable=True)
    risingstarbadge = Column(Boolean, nullable=True)

    def __repr__(self):
        return f"<DiscordEngagement(id={self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'contributor': self.contributor,
            'has_introduced': self.has_introduced,
            'total_message_count': self.total_message_count,
            'total_reaction_count': self.total_reaction_count,
            'converserbadge': self.converserbadge,
            'apprenticebadge': self.apprenticebadge,
            'rockstarbadge': self.rockstarbadge,
            'enthusiastbadge': self.enthusiastbadge,
            'risingstarbadge': self.risingstarbadge
        }

class DmpIssueUpdates(Base):
    __tablename__ = 'dmp_issue_updates'
    __table_args__ = {'comment': 'Having records of dmp with issue details'}

    created_at = Column(DateTime, nullable=False)
    body_text = Column(Text, nullable=True)
    comment_link = Column(Text, nullable=True)
    comment_id = Column(BigInteger, primary_key=True)
    comment_api = Column(String, nullable=True)
    comment_updated_at = Column(DateTime, nullable=True)
    dmp_id = Column(BigInteger, ForeignKey('dmp_issues.id'), nullable=False)
    created_by = Column(Text, nullable=False)

    def __repr__(self):
        return f"<DmpIssueUpdates(comment_id={self.comment_id})>"

    def to_dict(self):
        return {
            'created_at': self.created_at,
            'body_text': self.body_text,
            'comment_link': self.comment_link,
            'comment_id': self.comment_id,
            'comment_api': self.comment_api,
            'comment_updated_at': self.comment_updated_at,
            'dmp_id': self.dmp_id,
            'created_by': self.created_by
        }


class DmpIssues(Base):
    __tablename__ = 'dmp_issues'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    issue_url = Column(String, nullable=False)
    issue_number = Column(BigInteger, nullable=False)
    mentor_username = Column(Text, nullable=True)
    contributor_username = Column(Text, nullable=True)
    title = Column(Text, nullable=False)
    org_id = Column(BigInteger, ForeignKey('dmp_orgs.id'), nullable=False)
    description = Column(Text, nullable=False)
    repo = Column(Text, nullable=False)

    def __repr__(self):
        return f"<DmpIssues(id={self.id}, title={self.title})>"

    def to_dict(self):
        return {
            'id': self.id,
            'issue_url': self.issue_url,
            'issue_number': self.issue_number,
            'mentor_username': self.mentor_username,
            'contributor_username': self.contributor_username,
            'title': self.title,
            'org_id': self.org_id,
            'description': self.description,
            'repo': self.repo
        }

class DmpOrgs(Base):
    __tablename__ = 'dmp_orgs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    link = Column(Text, nullable=False)
    repo_owner = Column(Text, nullable=False)
    
    # issues = relationship('Issues', backref='organization', lazy='joined')


    def __repr__(self):
        return f"<DmpOrgs(id={self.id}, name={self.name})>"

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'name': self.name,
            'description': self.description,
            'link': self.link,
            'repo_owner': self.repo_owner
        }

class DmpPrUpdates(Base):
    __tablename__ = 'dmp_pr_updates'
    __table_args__ = {'comment': 'Having PR related records'}

    created_at = Column(DateTime, nullable=False)
    pr_id = Column(BigInteger, primary_key=True)
    status = Column(String, nullable=False)
    title = Column(Text, nullable=False)
    pr_updated_at = Column(DateTime, nullable=True)
    merged_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    dmp_id = Column(BigInteger, ForeignKey('dmp_issues.id'), nullable=False)
    link = Column(Text, nullable=False)

    def __repr__(self):
        return f"<DmpPrUpdates(pr_id={self.pr_id})>"

    def to_dict(self):
        return {
            'created_at': self.created_at,
            'pr_id': self.pr_id,
            'status': self.status,
            'title': self.title,
            'pr_updated_at': self.pr_updated_at,
            'merged_at': self.merged_at,
            'closed_at': self.closed_at,
            'dmp_id': self.dmp_id,
            'link': self.link
        }

class DmpTickets(Base):
    __tablename__ = 'dmp_tickets'

    created_at = Column(DateTime, nullable=True)
    name = Column(Text, nullable=True)
    product = Column(Text, nullable=True)
    complexity = Column(Text, nullable=True)
    project_category = Column(Text, nullable=True)
    project_sub_category = Column(Text, nullable=True)
    reqd_skills = Column(Text, nullable=True)
    issue_id = Column(BigInteger, unique=True, nullable=False)
    api_endpoint_url = Column(Text, unique=True, nullable=True)
    url = Column(Text, unique=True, nullable=True)
    ticket_points = Column(Integer, nullable=True, comment='How many points the ticket is worth')
    index = Column(Integer, unique=True, autoincrement=True)
    mentors = Column(Text, nullable=True)
    uuid = Column(UUID(as_uuid=True), primary_key=True)
    status = Column(Text, nullable=True)
    community_label = Column(Boolean, nullable=True, comment='has community label')
    organization = Column(Text, nullable=True)

    def __repr__(self):
        return f"<DmpTickets(uuid={self.uuid})>"

    def to_dict(self):
        return {
            'created_at': self.created_at,
            'name': self.name,
            'product': self.product,
            'complexity': self.complexity,
            'project_category': self.project_category,
            'project_sub_category': self.project_sub_category,
            'reqd_skills': self.reqd_skills,
            'issue_id': self.issue_id,
            'api_endpoint_url': self.api_endpoint_url,
            'url': self.url,
            'ticket_points': self.ticket_points,
            'index': self.index,
            'mentors': self.mentors,
            'uuid': self.uuid,
            'status': self.status,
            'community_label': self.community_label,
            'organization': self.organization
        }

class DmpWeekUpdates(Base):
    __tablename__ = 'dmp_week_updates'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    issue_url = Column(Text, nullable=False)
    week = Column(BigInteger, nullable=True)
    total_task = Column(BigInteger, nullable=True)
    completed_task = Column(BigInteger, nullable=True)
    progress = Column(Float, nullable=True)
    task_data = Column(Text, nullable=True)
    dmp_id = Column(BigInteger, nullable=True)

    def __repr__(self):
        return f"<DmpWeekUpdates(id={self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'issue_url': self.issue_url,
            'week': self.week,
            'total_task': self.total_task,
            'completed_task': self.completed_task,
            'progress': self.progress,
            'task_data': self.task_data,
            'dmp_id': self.dmp_id
        }

class GithubClassroomData(Base):
    __tablename__ = 'github_classroom_data'
    __table_args__ = {'comment': 'Table for saving the details about github classroom assignment data'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)
    assignment_name = Column(Text, nullable=False)
    assignment_url = Column(Text, nullable=False)
    assignment_id = Column(Text, nullable=True)
    starter_code_url = Column(Text, nullable=False)
    github_username = Column(Text, nullable=True)
    roster_identifier = Column(Text, nullable=True)
    student_repository_name = Column(Text, nullable=True)
    student_repository_url = Column(Text, nullable=True)
    submission_timestamp = Column(DateTime, nullable=False)
    points_awarded = Column(Integer, nullable=True)
    points_available = Column(Integer, nullable=True)
    c4gt_points = Column(Integer, nullable=True)
    discord_id = Column(Text, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<GithubClassroomData(id={self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'assignment_name': self.assignment_name,
            'assignment_url': self.assignment_url,
            'assignment_id': self.assignment_id,
            'starter_code_url': self.starter_code_url,
            'github_username': self.github_username,
            'roster_identifier': self.roster_identifier,
            'student_repository_name': self.student_repository_name,
            'student_repository_url': self.student_repository_url,
            'submission_timestamp': self.submission_timestamp,
            'points_awarded': self.points_awarded,
            'points_available': self.points_available,
            'c4gt_points': self.c4gt_points,
            'discord_id': self.discord_id,
            'updated_at': self.updated_at
        }

class GithubInstallations(Base):
    __tablename__ = 'github_installations'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    github_organisation = Column(Text, unique=True, nullable=False)
    installation_id = Column(BigInteger, unique=True, nullable=False)
    target_type = Column(Text, nullable=True, comment='Type of github entity that installed the app, usually "Organisation"')
    github_ids = Column(Text, nullable=True, comment="Identifiers on the github database, prolly won't be used")
    permissions_and_events = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    organisation = Column(Text, ForeignKey('community_organisations.name'), nullable=True)

    def __repr__(self):
        return f"<GithubInstallations(id={self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'github_organisation': self.github_organisation,
            'installation_id': self.installation_id,
            'target_type': self.target_type,
            'github_ids': self.github_ids,
            'permissions_and_events': self.permissions_and_events,
            'created_at': self.created_at,
            'organisation': self.organisation
        }
##

class GithubOrganisationsToOrganisations(Base):
    __tablename__ = 'github_organisations_to_organisations'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    github_organisation = Column(Text, nullable=False)
    organisation = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True, comment='Creation date of organization ticket')

    def __repr__(self):
        return f"<GithubOrganisationsToOrganisations(id={self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'github_organisation': self.github_organisation,
            'organisation': self.organisation,
            'created_at': self.created_at
        }

class IssueContributors(Base):
    __tablename__ = 'issue_contributors'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    contributor_id = Column(BigInteger, ForeignKey('contributors_registration.id'))
    issue_id = Column(BigInteger, ForeignKey('issues.id'), primary_key=True)
    role = Column(BigInteger, ForeignKey('role_master.id'), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<IssueContributors(contributor_id={self.contributor_id}, issue_id={self.issue_id})>"

    def to_dict(self):
        return {
            'contributor_id': self.contributor_id,
            'issue_id': self.issue_id,
            'role_id': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class IssueMentors(Base):
    __tablename__ = 'issue_mentors'

    issue_id = Column(BigInteger, ForeignKey('issues.id'), primary_key=True)
    mentor_id = Column(BigInteger, ForeignKey('mentor_details.id'), primary_key=True)
    createdat = Column(DateTime, nullable=True)
    updatedat = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<IssueMentors(issue_id={self.issue_id}, mentor_id={self.mentor_id})>"

    def to_dict(self):
        return {
            'issue_id': self.issue_id,
            'mentor_id': self.mentor_id,
            'createdat': self.createdat,
            'updatedat': self.updatedat
        }

class Issues(Base):
    __tablename__ = 'issues'

    id = Column(BigInteger, primary_key=True)
    link = Column(Text, nullable=False)
    labels = Column(Text, nullable=True)
    project_type = Column(Text, nullable=True)
    complexity = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)
    technology = Column(Text, nullable=True)
    status = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    org_id = Column(BigInteger, ForeignKey('community_orgs.id'), nullable=True)
    issue_id = Column(BigInteger, nullable=True)
    
    point_transactions = relationship('PointTransactions', back_populates='issue')
    user_activities = relationship('UserActivity', back_populates='issue')



    def __repr__(self):
        return f"<Issues(id={self.id}, title={self.title})>"
    

    def __repr__(self):
        return f"<Issues(id={self.id}, title={self.title})>"

    def to_dict(self):
        return {
            'id': self.id,
            'link': self.link,
            'labels': self.labels,
            'complexity': self.complexity,
            'skills': self.skills,
            'technology': self.technology,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'title': self.title,
            'description': self.description,
            'org_id': self.org_id,
            'issue_id': self.issue_id,
            'project_type':self.project_type
        }

class MentorDetails(Base):
    __tablename__ = 'mentor_details'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    discord_id = Column(String(255), nullable=True)
    discord_username = Column(String(255), nullable=True)
    github_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    point_transactions = relationship('PointTransactions', back_populates='mentor')
    user_activities = relationship('UserActivity', back_populates='mentor')
    user_points_mappings = relationship('UserPointsMapping', back_populates='mentor')



    def __repr__(self):
        return f"<MentorDetails(id={self.id}, name={self.name})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'discord_id': self.discord_id,
            'discord_username': self.discord_username,
            'github_id': self.github_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class MentorshipProgramSiteStructure(Base):
    __tablename__ = 'mentorship_program_site_structure'

    id = Column(BigInteger, primary_key=True)
    product_id = Column(BigInteger, ForeignKey('product.id'), nullable=True)
    project_id = Column(BigInteger, ForeignKey('mentorship_program_projects.id'), nullable=True)
    contributor_id = Column(BigInteger, ForeignKey('mentorship_program_selected_contributors.id'), nullable=True)
    website_directory_label = Column(Text, nullable=True)
    directory_url = Column(Text, nullable=True)

    # project = relationship('MentorshipProgramProjects', back_populates='site_structures')
    # contributor = relationship('MentorshipProgramSelectedContributors', back_populates='site_structures')

    def __repr__(self):
        return f"<MentorshipProgramSiteStructure(id={self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'project_id': self.project_id,
            'contributor_id': self.contributor_id,
            'website_directory_label': self.website_directory_label,
            'directory_url': self.directory_url
        }

class MentorshipProgramWebsiteComments(Base):
    __tablename__ = 'mentorship_program_website_comments'

    comment_id = Column(BigInteger, primary_key=True)
    url = Column(Text, nullable=True)
    html_url = Column(Text, nullable=True)
    commented_by_username = Column(Text, nullable=True)
    commented_by_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    body = Column(Text, nullable=True)
    pr_id = Column(BigInteger, nullable=True)

    def __repr__(self):
        return f"<MentorshipProgramWebsiteComments(comment_id={self.comment_id})>"

    def to_dict(self):
        return {
            'comment_id': self.comment_id,
            'url': self.url,
            'html_url': self.html_url,
            'commented_by_username': self.commented_by_username,
            'commented_by_id': self.commented_by_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'body': self.body,
            'pr_id': self.pr_id
        }

class MentorshipProgramWebsiteCommits(Base):
    __tablename__ = 'mentorship_program_website_commits'

    node_id = Column(Text, primary_key=True)
    url = Column(Text, nullable=True)
    html_url = Column(Text, nullable=True)
    comment_count = Column(Integer, nullable=True)
    date = Column(DateTime, nullable=True)
    author_id = Column(BigInteger, nullable=True)
    author_username = Column(Text, nullable=True)
    author_email = Column(Text, nullable=True)
    committer_id = Column(BigInteger, nullable=True)
    committer_username = Column(Text, nullable=True)
    committer_email = Column(Text, nullable=True)
    additions = Column(Integer, nullable=True)
    deletions = Column(Integer, nullable=True)
    files = Column(Text, nullable=True)
    project_folder_name = Column(Text, nullable=True)
    pr_id = Column(BigInteger, nullable=True)

    def __repr__(self):
        return f"<MentorshipProgramWebsiteCommits(node_id={self.node_id})>"

    def to_dict(self):
        return {
            'node_id': self.node_id,
            'url': self.url,
            'html_url': self.html_url,
            'comment_count': self.comment_count,
            'date': self.date,
            'author_id': self.author_id,
            'author_username': self.author_username,
            'author_email': self.author_email,
            'committer_id': self.committer_id,
            'committer_username': self.committer_username,
            'committer_email': self.committer_email,
            'additions': self.additions,
            'deletions': self.deletions,
            'files': self.files,
            'project_folder_name': self.project_folder_name,
            'pr_id': self.pr_id
        }

class MentorshipProgramWebsiteHasUpdated(Base):
    __tablename__ = 'mentorship_program_website_has_updated'

    id = Column(BigInteger, primary_key=True)
    project_id = Column(BigInteger, ForeignKey('mentorship_program_projects.id'), nullable=True)
    week1_update_date = Column(DateTime, nullable=True)
    week2_update_date = Column(DateTime, nullable=True)
    week3_update_date = Column(DateTime, nullable=True)
    week4_update_date = Column(DateTime, nullable=True)
    week5_update_date = Column(DateTime, nullable=True)
    week6_update_date = Column(DateTime, nullable=True)
    week7_update_date = Column(DateTime, nullable=True)
    week8_update_date = Column(DateTime, nullable=True)
    week9_update_date = Column(DateTime, nullable=True)
    week1_is_default_text = Column(Boolean, nullable=True)
    week2_is_default_text = Column(Boolean, nullable=True)
    week3_is_default_text = Column(Boolean, nullable=True)
    week4_is_default_text = Column(Boolean, nullable=True)
    week5_is_default_text = Column(Boolean, nullable=True)
    week6_is_default_text = Column(Boolean, nullable=True)
    week7_is_default_text = Column(Boolean, nullable=True)
    week8_is_default_text = Column(Boolean, nullable=True)
    week9_is_default_text = Column(Boolean, nullable=True)
    product = Column(Text, nullable=True)
    project_folder = Column(Text, unique=True, nullable=False)
    all_links = Column(Text, nullable=True)

    def __repr__(self):
        return f"<MentorshipProgramWebsiteHasUpdated(id={self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'week1_update_date': self.week1_update_date,
            'week2_update_date': self.week2_update_date,
            'week3_update_date': self.week3_update_date,
            'week4_update_date': self.week4_update_date,
            'week5_update_date': self.week5_update_date,
            'week6_update_date': self.week6_update_date,
            'week7_update_date': self.week7_update_date,
            'week8_update_date': self.week8_update_date,
            'week9_update_date': self.week9_update_date,
            'week1_is_default_text': self.week1_is_default_text,
            'week2_is_default_text': self.week2_is_default_text,
            'week3_is_default_text': self.week3_is_default_text,
            'week4_is_default_text': self.week4_is_default_text,
            'week5_is_default_text': self.week5_is_default_text,
            'week6_is_default_text': self.week6_is_default_text,
            'week7_is_default_text': self.week7_is_default_text,
            'week8_is_default_text': self.week8_is_default_text,
            'week9_is_default_text': self.week9_is_default_text,
            'product': self.product,
            'project_folder': self.project_folder,
            'all_links': self.all_links
        }



##

class MentorshipProgramWebsitePullRequest(Base):
    __tablename__ = 'mentorship_program_website_pull_request'

    pr_url = Column(Text, nullable=True)
    pr_id = Column(BigInteger, primary_key=True)
    pr_node_id = Column(Text, unique=True, nullable=True)
    html_url = Column(Text, nullable=True)
    status = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    raised_by_username = Column(Text, nullable=True)
    raised_by_id = Column(Integer, nullable=True)
    body = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    merged_at = Column(DateTime, nullable=True)
    assignees = Column(Text, nullable=True)
    requested_reviewers = Column(Text, nullable=True)
    labels = Column(Text, nullable=True)
    review_comments_url = Column(Text, nullable=True)
    comments_url = Column(Text, nullable=True)
    repository_id = Column(Integer, nullable=True)
    repository_owner_name = Column(Text, nullable=True)
    repository_owner_id = Column(Integer, nullable=True)
    repository_url = Column(Text, nullable=True)
    merged = Column(Boolean, nullable=True)
    number_of_commits = Column(Integer, nullable=True)
    number_of_comments = Column(Integer, nullable=True)
    lines_of_code_added = Column(Integer, nullable=True)
    lines_of_code_removed = Column(Integer, nullable=True)
    number_of_files_changed = Column(Integer, nullable=True)
    merged_by_id = Column(BigInteger, nullable=True)
    merged_by_username = Column(Text, nullable=True)
    linked_ticket = Column(Text, nullable=True)
    project_name = Column(Text, nullable=True)
    project_folder_label = Column(Text, nullable=True)
    week_number = Column(SmallInteger, nullable=True)

    def __repr__(self):
        return f"<MentorshipProgramWebsitePullRequest(pr_id={self.pr_id}, title={self.title})>"

    def to_dict(self):
        return {
            'pr_url': self.pr_url,
            'pr_id': self.pr_id,
            'pr_node_id': self.pr_node_id,
            'html_url': self.html_url,
            'status': self.status,
            'title': self.title,
            'raised_by_username': self.raised_by_username,
            'raised_by_id': self.raised_by_id,
            'body': self.body,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'closed_at': self.closed_at,
            'merged_at': self.merged_at,
            'assignees': self.assignees,
            'requested_reviewers': self.requested_reviewers,
            'labels': self.labels,
            'review_comments_url': self.review_comments_url,
            'comments_url': self.comments_url,
            'repository_id': self.repository_id,
            'repository_owner_name': self.repository_owner_name,
            'repository_owner_id': self.repository_owner_id,
            'repository_url': self.repository_url,
            'merged': self.merged,
            'number_of_commits': self.number_of_commits,
            'number_of_comments': self.number_of_comments,
            'lines_of_code_added': self.lines_of_code_added,
            'lines_of_code_removed': self.lines_of_code_removed,
            'number_of_files_changed': self.number_of_files_changed,
            'merged_by_id': self.merged_by_id,
            'merged_by_username': self.merged_by_username,
            'linked_ticket': self.linked_ticket,
            'project_name': self.project_name,
            'project_folder_label': self.project_folder_label,
            'week_number': self.week_number
        }

class MentorshipWebsiteContributorProject(Base):
    __tablename__ = 'mentorship_website_contributor_project'

    project_folder = Column(Text, primary_key=True)
    contributor = Column(Text, nullable=True)

    def __repr__(self):
        return f"<MentorshipWebsiteContributorProject(project_folder={self.project_folder})>"

    def to_dict(self):
        return {
            'project_folder': self.project_folder,
            'contributor': self.contributor
        }

class PointSystem(Base):
    __tablename__ = 'point_system'

    id = Column(BigInteger, primary_key=True)
    complexity = Column(Text, nullable=False)
    points = Column(SmallInteger, nullable=True)

    def __repr__(self):
        return f"<PointSystem(id={self.id}, complexity={self.complexity})>"

    def to_dict(self):
        return {
            'id': self.id,
            'complexity': self.complexity,
            'points': self.points
        }
        
class PointTransactions(Base):
    __tablename__ = 'point_transactions'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('contributors_registration.id'), nullable=True)
    issue_id = Column(BigInteger, ForeignKey('issues.id'), nullable=False)
    point = Column(Integer, nullable=True)
    type = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)  # Set to current time when created
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)  # Updated to current time when record is modified
    mentor_id = Column(BigInteger, ForeignKey('mentor_details.id'), nullable=True)

    
    contributor = relationship('ContributorsRegistration', back_populates='point_transactions')
    issue = relationship('Issues', back_populates='point_transactions')
    mentor = relationship('MentorDetails', back_populates='point_transactions')

    def __repr__(self):
        return f"<PointTransactions(id={self.id}, issue_id={self.issue_id})>"


    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'issue_id': self.issue_id,
            'point': self.point,
            'type': self.type,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'mentor_id': self.mentor_id
        }

class PointsMapping(Base):
    __tablename__ = 'points_mapping'

    id = Column(BigInteger, primary_key=True)
    role = Column(String(50), nullable=False)
    complexity = Column(String(50), nullable=False)
    points = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<PointsMapping(id={self.id}, role={self.role}, complexity={self.complexity})>"

    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'complexity': self.complexity,
            'points': self.points,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }



###

class PrHistory(Base):
    __tablename__ = 'pr_history'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=True)
    api_url = Column(Text, nullable=True)
    html_url = Column(Text, unique=True, nullable=True)
    raised_by = Column(BigInteger, nullable=True)
    raised_at = Column(DateTime, nullable=False)
    raised_by_username = Column(Text, nullable=False)
    status = Column(Text, nullable=True)
    is_merged = Column(Boolean, nullable=True)
    merged_by = Column(BigInteger, nullable=True)
    merged_at = Column(Text, nullable=True)
    merged_by_username = Column(Text, nullable=True)
    pr_id = Column(BigInteger, nullable=False)
    points = Column(SmallInteger, nullable=False)
    ticket_url = Column(Text, nullable=False)
    ticket_complexity = Column(Text, nullable=True)

    def __repr__(self):
        return f"<PrHistory(id={self.id}, pr_id={self.pr_id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'api_url': self.api_url,
            'html_url': self.html_url,
            'raised_by': self.raised_by,
            'raised_at': self.raised_at,
            'raised_by_username': self.raised_by_username,
            'status': self.status,
            'is_merged': self.is_merged,
            'merged_by': self.merged_by,
            'merged_at': self.merged_at,
            'merged_by_username': self.merged_by_username,
            'pr_id': self.pr_id,
            'points': self.points,
            'ticket_url': self.ticket_url,
            'ticket_complexity': self.ticket_complexity
        }

class PrStaging(Base):
    __tablename__ = 'pr_staging'

    id = Column(String(36), primary_key=True)  # UUID field
    created_at = Column(DateTime, nullable=True)
    api_url = Column(Text, nullable=True)
    html_url = Column(Text, unique=True, nullable=True)
    raised_by = Column(BigInteger, nullable=True)
    raised_at = Column(DateTime, nullable=False)
    raised_by_username = Column(Text, nullable=False)
    status = Column(Text, nullable=True)
    is_merged = Column(Boolean, nullable=True)
    merged_by = Column(BigInteger, nullable=True)
    merged_at = Column(Text, nullable=True)
    merged_by_username = Column(Text, nullable=True)
    pr_id = Column(BigInteger, nullable=False)
    points = Column(SmallInteger, nullable=False)
    ticket_url = Column(Text, nullable=False)
    ticket_complexity = Column(Text, nullable=True)

    def __repr__(self):
        return f"<PrStaging(id={self.id}, pr_id={self.pr_id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'api_url': self.api_url,
            'html_url': self.html_url,
            'raised_by': self.raised_by,
            'raised_at': self.raised_at,
            'raised_by_username': self.raised_by_username,
            'status': self.status,
            'is_merged': self.is_merged,
            'merged_by': self.merged_by,
            'merged_at': self.merged_at,
            'merged_by_username': self.merged_by_username,
            'pr_id': self.pr_id,
            'points': self.points,
            'ticket_url': self.ticket_url,
            'ticket_complexity': self.ticket_complexity
        }

class Product(Base):
    __tablename__ = 'product'

    id = Column(BigInteger, primary_key=True)  # Auto field
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    wiki_url = Column(Text, nullable=True)
    channel_id = Column(BigInteger, ForeignKey('discord_channels.channel_id'), nullable=True)  # Assumes 'DiscordChannels' model

    channel = relationship('DiscordChannels', back_populates='products')


    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'wiki_url': self.wiki_url,
            'channel_id': self.channel_id
        }

class RoleMaster(Base):
    __tablename__ = 'role_master'

    id = Column(BigInteger, primary_key=True)  # Auto field
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    role = Column(Text, nullable=True)

    def __repr__(self):
        return f"<RoleMaster(id={self.id}, role={self.role})>"

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'role': self.role
        }

class TicketComments(Base):
    __tablename__ = 'ticket_comments'

    id = Column(BigInteger, primary_key=True)
    url = Column(Text, nullable=True)
    html_url = Column(Text, nullable=True)
    issue_url = Column(Text, nullable=True)
    node_id = Column(Text, nullable=True)
    commented_by = Column(Text, nullable=True)
    commented_by_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    content = Column(Text, nullable=True)
    reactions_url = Column(Text, nullable=True)
    ticket_url = Column(Text, nullable=False)

    def __repr__(self):
        return f"<TicketComments(id={self.id}, ticket_url={self.ticket_url})>"

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'html_url': self.html_url,
            'issue_url': self.issue_url,
            'node_id': self.node_id,
            'commented_by': self.commented_by,
            'commented_by_id': self.commented_by_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'content': self.content,
            'reactions_url': self.reactions_url,
            'ticket_url': self.ticket_url
        }

class UnlistedTickets(Base):
    __tablename__ = 'unlisted_tickets'

    created_at = Column(DateTime, nullable=True)
    name = Column(Text, nullable=True)
    product = Column(Text, nullable=True)
    complexity = Column(Text, nullable=True)
    project_category = Column(Text, nullable=True)
    project_sub_category = Column(Text, nullable=True)
    reqd_skills = Column(Text, nullable=True)
    issue_id = Column(BigInteger, unique=True, nullable=False)
    api_endpoint_url = Column(Text, unique=True, nullable=True)
    url = Column(Text, unique=True, nullable=True)
    ticket_points = Column(SmallInteger, nullable=True)
    index = Column(SmallInteger, unique=True, nullable=False)
    mentors = Column(Text, nullable=True)
    uuid = Column(String(36), primary_key=True)  # UUID field
    status = Column(Text, nullable=True)
    organization = Column(Text, nullable=True)

    __table_args__ = (UniqueConstraint('uuid', 'issue_id'),)

    def __repr__(self):
        return f"<UnlistedTickets(uuid={self.uuid}, issue_id={self.issue_id})>"

    def to_dict(self):
        return {
            'created_at': self.created_at,
            'name': self.name,
            'product': self.product,
            'complexity': self.complexity,
            'project_category': self.project_category,
            'project_sub_category': self.project_sub_category,
            'reqd_skills': self.reqd_skills,
            'issue_id': self.issue_id,
            'api_endpoint_url': self.api_endpoint_url,
            'url': self.url,
            'ticket_points': self.ticket_points,
            'index': self.index,
            'mentors': self.mentors,
            'uuid': self.uuid,
            'status': self.status,
            'organization': self.organization
        }

class UnstructuredDiscordData(Base):
    __tablename__ = 'unstructured_discord_data'

    text = Column(Text, nullable=True)
    author = Column(BigInteger, nullable=True)
    channel = Column(BigInteger, nullable=True)
    channel_name = Column(Text, nullable=True)
    uuid = Column(String(36), primary_key=True)  # UUID field
    author_name = Column(Text, nullable=True)
    author_roles = Column(Text, nullable=True)
    sent_at = Column(Text, nullable=True)

    def __repr__(self):
        return f"<UnstructuredDiscordData(uuid={self.uuid}, author_name={self.author_name})>"

    def to_dict(self):
        return {
            'text': self.text,
            'author': self.author,
            'channel': self.channel,
            'channel_name': self.channel_name,
            'uuid': self.uuid,
            'author_name': self.author_name,
            'author_roles': self.author_roles,
            'sent_at': self.sent_at
        }

class UserActivity(Base):
    __tablename__ = 'user_activity'

    id = Column(UUID(as_uuid=True), primary_key=True)
    contributor_id = Column(BigInteger, ForeignKey('contributors_registration.id'), nullable=False)  # Assumes 'ContributorsRegistration' model
    issue_id = Column(BigInteger, ForeignKey('issues.id'), nullable=False)  # Assumes 'Issues' model
    activity = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    mentor_id = Column(BigInteger, ForeignKey('mentor_details.id'), nullable=True)  # Assumes 'MentorDetails' model

    contributor = relationship('ContributorsRegistration', back_populates='user_activities')
    issue = relationship('Issues', back_populates='user_activities')
    mentor = relationship('MentorDetails', back_populates='user_activities')

    def __repr__(self):
        return f"<UserActivity(contributor_id={self.contributor_id}, issue_id={self.issue_id})>"

    def to_dict(self):
        return {
            'contributor_id': self.contributor_id,
            'issue_id': self.issue_id,
            'activity': self.activity,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'mentor_id': self.mentor_id
        }

class UserBadges(Base):
    __tablename__ = 'user_badges'
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)  # Assumes 'Users' model
    badge_id = Column(BigInteger, ForeignKey('badges.id'), nullable=False)  # Assumes 'Badges' model
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    user = relationship('Users', back_populates='user_badges')
    badge = relationship('Badges', back_populates='user_badges')

    def __repr__(self):
        return f"<UserBadges(user_id={self.user_id}, badge_id={self.badge_id})>"

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class UserCertificates(Base):
    __tablename__ = 'user_certificates'
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)  # Assumes 'Users' model
    certificate_link = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    user = relationship('Users', back_populates='user_certificates')

    def __repr__(self):
        return f"<UserCertificates(user_id={self.user_id}, certificate_link={self.certificate_link})>"

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'certificate_link': self.certificate_link,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }



###

class UserPointsMapping(Base):
    __tablename__ = 'user_points_mapping'
    id = Column(UUID(as_uuid=True), primary_key=True)
    contributor = Column(BigInteger, ForeignKey('contributors_registration.id'), nullable=True)  # Assumes 'ContributorsRegistration' model
    points = Column(Integer, nullable=False)
    level = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)  # Set to current time when created
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    mentor_id = Column(BigInteger, ForeignKey('mentor_details.id'), nullable=True)  # Assumes 'MentorDetails' model

    contributors = relationship('ContributorsRegistration', back_populates='user_points_mappings')
    mentor = relationship('MentorDetails', back_populates='user_points_mappings')

    def __repr__(self):
        return f"<UserPointsMapping(contributor_id={self.contributor}, points={self.points}, level={self.level})>"

    def to_dict(self):
        return {
            'contributor_id': self.contributor,
            'points': self.points,
            'level': self.level,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'mentor_id': self.mentor_id
        }

class Users(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)  # Assumes id is the primary key
    name = Column(Text, nullable=True)
    discord = Column(Text, unique=True, nullable=True)
    github = Column(Text, nullable=True)
    points = Column(Integer, nullable=True)
    level = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    user_badges = relationship('UserBadges', back_populates='user')
    user_certificates = relationship('UserCertificates', back_populates='user')


    def __repr__(self):
        return f"<Users(id={self.id}, name={self.name}, discord={self.discord})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'discord': self.discord,
            'github': self.github,
            'points': self.points,
            'level': self.level,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class VcLogs(Base):
    __tablename__ = 'vc_logs'

    id = Column(BigInteger, primary_key=True)  # Auto field
    created_at = Column(DateTime, nullable=False)
    discord_id = Column(BigInteger, nullable=True)
    discord_name = Column(Text, nullable=True)
    option = Column(Text, nullable=True)

    def __repr__(self):
        return f"<VcLogs(id={self.id}, discord_name={self.discord_name}, option={self.option})>"

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'discord_id': self.discord_id,
            'discord_name': self.discord_name,
            'option': self.option
        }

class GitHubProfileData(Base):
    __tablename__ = 'github_profile_data'
    
    github_username = Column(String, primary_key=True)
    discord_id = Column(BigInteger, nullable=False)
    classroom_points = Column(Integer, nullable=False, default=0)
    prs_raised = Column(Integer, nullable=False, default=0)
    prs_reviewed = Column(Integer, nullable=False, default=0)
    prs_merged = Column(Integer, nullable=False, default=0)
    dpg_points = Column(Integer, nullable=False, default=0)
    milestone = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<GitHubProfileData(github_username={self.github_username})>"

    def to_dict(self):
        return {
            'github_username': self.github_username,
            'discord_id': self.discord_id,
            'classroom_points': self.classroom_points,
            'prs_raised': self.prs_raised,
            'prs_reviewed': self.prs_reviewed,
            'prs_merged': self.prs_merged,
            'dpg_points': self.dpg_points,
            'milestone': self.milestone,
        }

class CommunityOrgs(Base):
    __tablename__ = 'community_orgs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=True)

    def __repr__(self):
        return f"<CommunityOrgs(name={self.name})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }