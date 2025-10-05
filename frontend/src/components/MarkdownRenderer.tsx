'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export default function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Customize heading styles
          h1: ({ children }) => (
            <h1 className="text-xl font-bold text-gray-800 mb-3 mt-4 first:mt-0">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold text-gray-800 mb-2 mt-3 first:mt-0">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-semibold text-gray-800 mb-2 mt-2 first:mt-0">
              {children}
            </h3>
          ),
          
          // Customize paragraph styles
          p: ({ children }) => (
            <p className="text-sm sm:text-base text-gray-700 mb-2 leading-relaxed">
              {children}
            </p>
          ),
          
          // Customize list styles
          ul: ({ children }) => (
            <ul className="list-disc list-inside text-sm sm:text-base text-gray-700 mb-2 space-y-1">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside text-sm sm:text-base text-gray-700 mb-2 space-y-1">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-sm sm:text-base text-gray-700">
              {children}
            </li>
          ),
          
          // Customize code styles
          code: ({ children, className }) => {
            const isInline = !className;
            if (isInline) {
              return (
                <code className="bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-xs font-mono">
                  {children}
                </code>
              );
            }
            return (
              <code className="block bg-gray-100 text-gray-800 p-2 rounded text-xs font-mono overflow-x-auto">
                {children}
              </code>
            );
          },
          pre: ({ children }) => (
            <pre className="bg-gray-100 text-gray-800 p-3 rounded text-xs font-mono overflow-x-auto mb-2">
              {children}
            </pre>
          ),
          
          // Customize blockquote styles
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-blue-300 pl-3 italic text-gray-600 mb-2">
              {children}
            </blockquote>
          ),
          
          // Customize link styles
          a: ({ children, href }) => (
            <a 
              href={href} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {children}
            </a>
          ),
          
          // Customize table styles
          table: ({ children }) => (
            <div className="overflow-x-auto mb-2">
              <table className="min-w-full border border-gray-300 text-xs sm:text-sm">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-gray-50">
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody className="bg-white">
              {children}
            </tbody>
          ),
          tr: ({ children }) => (
            <tr className="border-b border-gray-200">
              {children}
            </tr>
          ),
          th: ({ children }) => (
            <th className="px-2 py-1 text-left font-semibold text-gray-700 border-r border-gray-300">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-2 py-1 text-gray-700 border-r border-gray-300">
              {children}
            </td>
          ),
          
          // Customize strong and emphasis
          strong: ({ children }) => (
            <strong className="font-semibold text-gray-800">
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em className="italic text-gray-700">
              {children}
            </em>
          ),
          
          // Customize horizontal rule
          hr: () => (
            <hr className="border-gray-300 my-3" />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
