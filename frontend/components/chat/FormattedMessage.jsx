'use client'

/**
 * FormattedMessage - Renders AI chat messages with beautiful formatting
 * Supports: **bold**, bullet lists, numbered lists, line breaks
 */
const FormattedMessage = ({ text }) => {
    if (!text) return null;

    const formatText = (content) => {
        const lines = content.split('\n');
        const elements = [];
        let listItems = [];
        let listType = null; // 'bullet' or 'numbered'

        lines.forEach((line, index) => {
            const trimmedLine = line.trim();

            // Check if this is a list item
            const bulletMatch = trimmedLine.match(/^[-•]\s*(.+)/);
            const numberedMatch = trimmedLine.match(/^\d+\.\s*(.+)/);

            if (bulletMatch) {
                if (listType !== 'bullet') {
                    // Flush any previous list
                    if (listItems.length > 0) {
                        elements.push(renderList(listItems, listType, `list-${elements.length}`));
                        listItems = [];
                    }
                    listType = 'bullet';
                }
                listItems.push(bulletMatch[1]);
            } else if (numberedMatch) {
                if (listType !== 'numbered') {
                    // Flush any previous list
                    if (listItems.length > 0) {
                        elements.push(renderList(listItems, listType, `list-${elements.length}`));
                        listItems = [];
                    }
                    listType = 'numbered';
                }
                listItems.push(numberedMatch[1]);
            } else {
                // Regular line - flush any ongoing list first
                if (listItems.length > 0) {
                    elements.push(renderList(listItems, listType, `list-${elements.length}`));
                    listItems = [];
                    listType = null;
                }

                if (trimmedLine) {
                    // Process bold text and render the line
                    elements.push(
                        <p key={`p-${index}`} className="mb-3 last:mb-0 leading-relaxed">
                            {processBoldText(trimmedLine)}
                        </p>
                    );
                }
            }
        });

        // Flush any remaining list items
        if (listItems.length > 0) {
            elements.push(renderList(listItems, listType, `list-${elements.length}`));
        }

        return elements;
    };

    const renderList = (items, type, key) => {
        const ListTag = type === 'numbered' ? 'ol' : 'ul';
        const listClass = type === 'numbered'
            ? 'list-decimal list-inside space-y-2 mb-3 ml-2'
            : 'list-disc list-inside space-y-2 mb-3 ml-2';

        return (
            <ListTag key={key} className={listClass}>
                {items.map((item, i) => (
                    <li key={i} className="text-slate-700 leading-relaxed pl-2">
                        {processBoldText(item)}
                    </li>
                ))}
            </ListTag>
        );
    };

    const processBoldText = (text) => {
        // Split by **text** pattern
        const parts = text.split(/(\*\*.*?\*\*)/g);

        return parts.map((part, i) => {
            if (part.startsWith('**') && part.endsWith('**')) {
                // Bold text
                const boldText = part.slice(2, -2);
                return (
                    <strong key={i} className="font-semibold text-slate-900">
                        {boldText}
                    </strong>
                );
            }
            return <span key={i}>{part}</span>;
        });
    };

    return (
        <div className="text-[15px] text-slate-700 leading-relaxed">
            {formatText(text)}
        </div>
    );
};

export default FormattedMessage;
