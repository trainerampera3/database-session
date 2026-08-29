import React, {
    useEffect,
    useState
} from "react";

import {
    MdOpenInNew,
    MdSearch,
    MdRefresh,
    MdArticle
} from "react-icons/md";

import {
    getNews
} from "../services/api";


function News() {

    const [news, setNews] =
        useState([]);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");

    const [search, setSearch] =
        useState("");


    async function loadNews() {

        try {

            setLoading(true);
            setError("");

            const response =
                await getNews(50, 0);

            setNews(
                response?.data || []
            );

        } catch (error) {

            console.error(
                "News loading failed:",
                error
            );

            setError(
                "Unable to load weather news."
            );

            setNews([]);

        } finally {

            setLoading(false);

        }

    }


    useEffect(() => {

        loadNews();

    }, []);


    const filteredNews =
        news.filter((article) => {

            const searchText =
                search.toLowerCase();

            return (

                article.title
                    ?.toLowerCase()
                    .includes(searchText)

                ||

                article.description
                    ?.toLowerCase()
                    .includes(searchText)

                ||

                article.source
                    ?.toLowerCase()
                    .includes(searchText)

            );

        });


    function formatDate(date) {

        if (!date) {
            return "Unknown date";
        }

        return new Date(date)
            .toLocaleString(
                "en-IN",
                {
                    dateStyle: "medium",
                    timeStyle: "short"
                }
            );

    }


    return (

        <section className="page news-page">

            {/* Header */}

            <div className="page__heading">

                <div>

                    <h2>
                        Weather News
                    </h2>

                    <p>
                        Latest weather-related
                        news collected by the ETL pipeline.
                    </p>

                </div>


                <button
                    className="news-refresh-button"
                    onClick={loadNews}
                    disabled={loading}
                >

                    <MdRefresh />

                    {loading
                        ? "Refreshing..."
                        : "Refresh"}

                </button>

            </div>


            {/* Search */}

            <div className="news-toolbar">

                <div className="news-search">

                    <MdSearch />

                    <input
                        type="text"
                        placeholder="Search weather news..."
                        value={search}
                        onChange={(event) =>
                            setSearch(
                                event.target.value
                            )
                        }
                    />

                </div>


                <div className="news-count">

                    <MdArticle />

                    <span>
                        {filteredNews.length} articles
                    </span>

                </div>

            </div>


            {/* Error */}

            {error && (

                <div className="news-error">

                    {error}

                    <button
                        onClick={loadNews}
                    >
                        Try again
                    </button>

                </div>

            )}


            {/* Loading */}

            {loading && !error && (

                <div className="news-loading">

                    <div className="news-spinner"></div>

                    <p>
                        Loading weather news...
                    </p>

                </div>

            )}


            {/* Empty */}

            {!loading &&
                !error &&
                filteredNews.length === 0 && (

                    <div className="news-empty">

                        <MdArticle />

                        <h3>
                            No news found
                        </h3>

                        <p>
                            Try a different search term.
                        </p>

                    </div>

                )}


            {/* News grid */}

            {!loading &&
                !error &&
                filteredNews.length > 0 && (

                    <div className="news-grid">

                        {filteredNews.map(
                            (article) => (

                                <article
                                    className="news-card"
                                    key={article.news_id}
                                >

                                    <div className="news-card__top">

                                        <span className="news-card__source">

                                            {article.source}

                                        </span>

                                        <span className="news-card__date">

                                            {formatDate(
                                                article.published_at
                                            )}

                                        </span>

                                    </div>


                                    <h3 className="news-card__title">

                                        {article.title}

                                    </h3>


                                    {article.description && (

                                        <p className="news-card__description">

                                            {article.description}

                                        </p>

                                    )}


                                    <div className="news-card__footer">

                                        <span>
                                            Weather News
                                        </span>


                                        {article.url && (

                                            <a
                                                href={article.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="news-card__link"
                                            >

                                                Read article

                                                <MdOpenInNew />

                                            </a>

                                        )}

                                    </div>

                                </article>

                            )
                        )}

                    </div>

                )}

        </section>

    );

}

export default News;