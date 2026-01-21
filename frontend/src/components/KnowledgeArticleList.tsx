/**
 * Knowledge article list component.
 */

import { DocumentTextIcon } from '@heroicons/react/24/outline';
import type { KnowledgeArticle } from '../types';

interface KnowledgeArticleListProps {
  articles: KnowledgeArticle[];
}

export function KnowledgeArticleList({ articles }: KnowledgeArticleListProps) {
  if (articles.length === 0) return null;

  return (
    <div
      className="rounded-lg border border-gray-200 bg-gray-50 overflow-hidden"
      role="region"
      aria-label="Related help articles"
    >
      <div className="px-3 py-2 bg-gray-100 border-b border-gray-200">
        <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
          Helpful Articles
        </h4>
      </div>

      <ul className="divide-y divide-gray-200">
        {articles.map((article) => {
          const hasValidUrl = article.url && article.url !== '#';
          const content = (
            <>
              <DocumentTextIcon
                className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5"
                aria-hidden="true"
              />
              <div className="min-w-0 flex-1">
                <p className={`text-sm font-medium truncate ${hasValidUrl ? 'text-primary-600 hover:text-primary-700' : 'text-gray-900'}`}>
                  {article.title}
                </p>
                {article.snippet && (
                  <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                    {article.snippet}
                  </p>
                )}
              </div>
              <RelevanceBadge score={article.relevance_score} />
            </>
          );

          return (
            <li key={article.article_id}>
              {hasValidUrl ? (
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-start gap-3 px-3 py-2 hover:bg-white transition-colors focus:outline-none focus:bg-white focus:ring-2 focus:ring-inset focus:ring-primary-500"
                >
                  {content}
                </a>
              ) : (
                <div className="flex items-start gap-3 px-3 py-2">
                  {content}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function RelevanceBadge({ score }: { score: number }) {
  // Only show for high relevance
  if (score < 0.8) return null;

  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success-100 text-success-800"
      aria-label={`${Math.round(score * 100)}% relevant`}
    >
      Best match
    </span>
  );
}
