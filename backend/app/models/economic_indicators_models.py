import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID, BIGINT
from sqlalchemy.sql import func
from app.models.base import Base

class NewsArticle(Base):

    __tablename__="NewsArticles"

    article_id = Column("article_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    datasource_id = Column("datasource_id", UUID(as_uuid=True), ForeignKey("DataSources.datasource_id"), nullable=False)
    entity_id = Column("entity_id", UUID(as_uuid=True), ForeignKey("Entities.entity_id"), nullable=False)
    url_hash = Column("url_hash", String)
    title = Column("title", String)
    author = Column("author", String)
    published_at = Column("published_at", DateTime, default=None)
    fetched_at = Column("fetched_at", DateTime, default=None)
    sentiment_score = Column("sentiment_score", Float)
    status = Column("status", String)

    def __init__(
        self, article_id, datasource_id, entity_id, url_hash,
        title, author, published_at, fetched_at, sentiment_score, status
    ) -> None:

        self.article_id = article_id
        self.datasource_id = datasource_id
        self.entity_id = entity_id
        self.url_hash = url_hash
        self.title = title
        self.author = author
        self.published_at = published_at
        self.fetched_at = fetched_at
        self.sentiment_score = sentiment_score
        self.status = status

    def __repr__(self) -> str:
        return f"{self.article_id} - {self.datasource_id} - {self.entity_id} - {self.url_hash} - {self.title} - {self.fetched_at} - {self.sentiment_score} - {self.status}"


class AnalystCommentary(Base):

    __tablename__="AnalystCommentary"

    commentary_id = Column("commentary_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    entity_id = Column("entity_id", UUID(as_uuid=True), ForeignKey("Entities.entity_id"), nullable=False)
    datasource_id = Column("datasource_id", UUID(as_uuid=True), ForeignKey("DataSources.datasource_id"), nullable=False)
    content = Column("content", String)
    analyst_name = Column("analyst_name", String)
    rating = Column("rating", String)
    price_target = Column("price_target", Numeric(precision=12, scale=2))
    published_at = Column("published_at", DateTime, default=None)
    fetched_at = Column("fetched_at", DateTime, default=None)
    expires_at = Column("expires_at", DateTime, default=None)
    status = Column("status", String)

    def __init__(self, commentary_id, entity_id, datasource_id, content, analyst_name,
                rating, price_target, published_at, fetched_at, expires_at, status
    ) -> None:
        
        self.commentary_id = commentary_id
        self.entity_id = entity_id
        self.datasource_id = datasource_id
        self.content = content
        self.analyst_name = analyst_name
        self.rating = rating
        self.price_target = price_target
        self.published_at = published_at
        self.fetched_at = fetched_at
        self.expires_at = expires_at
        self.status = status

    def __repr__(self) -> str:
        return f"{self.commentary_id} - {self.datasource_id} - {self.entity_id} - {self.content} - {self.rating} - {self.fetched_at} - {self.expires_at} - {self.status}"


class EconomicIndicatorRelease(Base):

    __tablename__="EconomicIndicatorReleases"

    release_id = Column("release_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    datasource_id = Column("datasource_id", UUID(as_uuid=True), ForeignKey("DataSources.datasource_id"), nullable=False)
    series_id = Column("series_id", String)
    indicador_name = Column("indicador_name", String)
    release_date = Column("release_date", DateTime)
    value = Column("value", Numeric(precision=12, scale=2))
    unit = Column("unit", String)
    fetched_at = Column("fetched_at", DateTime, default=None)

    def __init__(self, release_id, datasource_id, series_id, indicador_name,
                release_date, value, unit, fetched_at
    ) -> None:
        
        self.release_id = release_id
        self.datasource_id = datasource_id
        self.series_id = series_id
        self.indicador_name = indicador_name
        self.release_date = release_date
        self.value = value
        self.unit = unit
        self.fetched_at = fetched_at
        

    def __repr__(self) -> str:
        return f"{self.release_id} - {self.datasource_id} - {self.series_id} - {self.indicador_name} - {self.release_date} - {self.value} - {self.unit} - {self.fetched_at}"

class SECFiling(Base):

    __tablename__="SECFilings"

    filling_id = Column("filling_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    entity_id = Column("entity_id", UUID(as_uuid=True), ForeignKey("Entities.entity_id"), nullable=False)
    accession_number = Column("accession_number", String)
    filling_type = Column("filling_type", String)
    filed_at = Column("filed_at", DateTime)
    fetched_at = Column("fetched_at", DateTime, default=None)
    content = Column("content", String)
    filing_url = Column("filing_url", String)
    status = Column("status", String)

    def __init__(self, filling_id, entity_id, accession_number, filling_type,
                filed_at, fetched_at, content, filing_url, status
    ) -> None:
        
        self.filling_id = filling_id
        self.entity_id = entity_id
        self.accession_number = accession_number
        self.filling_type = filling_type
        self.filed_at = filed_at
        self.fetched_at = fetched_at
        self.content = content
        self.filing_url = filing_url
        self.status = status

    def __repr__(self) -> str:
        return f"{self.filling_id} - {self.entity_id} - {self.accession_number} - {self.filling_type} - {self.filed_at} - {self.content} - {self.filing_url} - {self.fetched_at} - {self.status}"

class OHLCVPrice(Base):

    __tablename__="OHLCVPrices"

    price_id = Column("price_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    entity_id = Column("entity_id", UUID(as_uuid=True), ForeignKey("Entities.entity_id"), nullable=False)
    trading_date = Column("trading_date", Date(timezone=True), server_default=func.now(), nullable=False)
    open = Column("open", Numeric(precision=12, scale=2))
    high = Column("high", Numeric(precision=12, scale=2))
    low = Column("low", Numeric(precision=12, scale=2))
    close = Column("close", Numeric(precision=12, scale=2))
    volume = Column("volume", BIGINT)
    fetched_at = Column("fetched_at", DateTime, default=None)

    def __init__(self, price_id, entity_id, trading_date, open,
                high, low, close, volume, fetched_at
    ) -> None:

        self.price_id = price_id
        self.entity_id = entity_id
        self.trading_date = trading_date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.fetched_at = fetched_at

    
    def __repr__(self) -> str:
        return f"{self.price_id} - {self.entity_id} - {self.trading_date} - {self.open} - {self.high} - {self.low} - {self.close} - {self.volume} - {self.fetched_at}"
