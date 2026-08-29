import React, { useEffect, useState } from "react";
import { MdArticle, MdOpenInNew } from "react-icons/md";

import { getNews } from "../services/api";


function LatestNewsMarquee() {

    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);


    useEffect(() => {

        async function loadNews() {

            try {

                const response = await getNews(5, 0);

                setNews(
                    Array.isArray(response)
                        ? response
                        : response?.data || []
                );

            } catch (error) {

                console.error(
                    "Failed to load weather news:",
                    error
                );

                setNews([]);

            } finally {

                setLoading(false);

            }

        }

        loadNews();

    }, []);


    if (loading) {

        return (
            <div className="news-marquee">

                <div className="news-marquee__label">

                    <MdArticle />

                    <span>Weather News</span>

                </div>

                <div className="news-marquee__content">

                    Loading latest news...

                </div>

            </div>
        );

    }


    if (news.length === 0) {

        return (
            <div className="news-marquee">

                <div className="news-marquee__label">

                    <MdArticle />

                    <span>Weather News</span>

                </div>

                <div className="news-marquee__content">

                    No weather news available.

                </div>

            </div>
        );

    }


    const marqueeItems = [...news, ...news];

    return (

        <div className="news-marquee">

            {/* Label */}

            <div className="news-marquee__label">

                <MdArticle />

                <span>Weather News</span>

            </div>


            {/* Scrolling area */}

            <div className="news-marquee__viewport">

                <div className="news-marquee__track">

                    {marqueeItems.map((article, index) => (

                        <a
                            key={`${article.news_id || index}-${index}`}
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="news-marquee__item"
                        >

                            <span className="news-marquee__dot">
                                ●
                            </span>

                            <span className="news-marquee__title">

                                {article.title}

                            </span>

                            <span className="news-marquee__source">

                                {article.source}

                            </span>

                            <MdOpenInNew
                                className="news-marquee__external"
                            />

                        </a>

                    ))}

                </div>

            </div>

        </div>

    );

}


export default LatestNewsMarquee;