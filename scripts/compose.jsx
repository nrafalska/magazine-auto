/*
compose.jsx
ExtendScript для автоматичної збірки журналу в InDesign
Читає plan.json і створює журнал з шаблонів
*/

// Головна функція
function main() {
    try {
        // Отримуємо шлях до plan.json зі змінної середовища
        var planPath = $.getenv('MAGAZINE_PLAN_PATH');
        
        if (!planPath) {
            alert('Помилка: Шлях до plan.json не знайдено');
            return;
        }
        
        var planFile = new File(planPath);
        if (!planFile.exists) {
            alert('Помилка: Файл не існує: ' + planPath);
            return;
        }
        
        // Читаємо план
        planFile.open('r');
        var planJSON = planFile.read();
        planFile.close();
        
        var plan = eval('(' + planJSON + ')');
        
        // Створюємо журнал
        var magazine = createMagazine(plan);
        
        if (magazine) {
            // Експортуємо результати
            var outputDir = planFile.parent;
            exportResults(magazine, outputDir, plan.project_name);
            
            alert('Готово! Журнал створено успішно.');
        }
        
    } catch (e) {
        alert('Помилка: ' + e.message + '\n' + e.line);
    }
}

// Створює новий документ журналу
function createMagazine(plan) {
    // Налаштування документу A4
    var doc = app.documents.add({
        documentPreferences: {
            pageWidth: '210mm',
            pageHeight: '297mm',
            facingPages: true,
            pageOrientation: PageOrientation.PORTRAIT
        }
    });
    
    // Базова папка з шаблонами
    var templatesDir = new Folder($.fileName).parent.parent + '/templates';
    
    // Обробляємо кожну сторінку з плану
    for (var i = 0; i < plan.pages.length; i++) {
        var pageData = plan.pages[i];
        
        try {
            if (pageData.template.indexOf('cover') !== -1) {
                // Обкладинка
                addCoverPage(doc, pageData, templatesDir);
            } else if (pageData.template.indexOf('spread') !== -1) {
                // Розворот
                addSpreadPages(doc, pageData, templatesDir);
            }
        } catch (e) {
            $.writeln('Помилка при додаванні сторінки ' + i + ': ' + e.message);
        }
    }
    
    return doc;
}

// Додає обкладинку
function addCoverPage(doc, pageData, templatesDir) {
    var templateFile = new File(templatesDir + '/' + pageData.template_file);
    
    if (!templateFile.exists) {
        $.writeln('Шаблон не знайдено: ' + templateFile);
        return;
    }
    
    // Відкриваємо шаблон
    var templateDoc = app.open(templateFile);
    var sourcePage = templateDoc.pages[pageData.page - 1];
    
    // Копіюємо сторінку
    sourcePage.duplicate(LocationOptions.AT_END, doc);
    var targetPage = doc.pages[doc.pages.length - 1];
    
    // Заповнюємо контентом
    fillCoverContent(targetPage, pageData.data);
    
    // Закриваємо шаблон
    templateDoc.close(SaveOptions.NO);
}

// Додає розворот
function addSpreadPages(doc, pageData, templatesDir) {
    var templateFile = new File(templatesDir + '/' + pageData.template_file);
    
    if (!templateFile.exists) {
        $.writeln('Шаблон не знайдено: ' + templateFile);
        return;
    }
    
    // Відкриваємо шаблон
    var templateDoc = app.open(templateFile);
    
    // Копіюємо обидві сторінки розвороту
    for (var i = 0; i < pageData.pages.length; i++) {
        var pageNum = pageData.pages[i];
        var sourcePage = templateDoc.pages[pageNum - 1];
        sourcePage.duplicate(LocationOptions.AT_END, doc);
    }
    
    // Заповнюємо контентом
    var leftPage = doc.pages[doc.pages.length - 2];
    var rightPage = doc.pages[doc.pages.length - 1];
    
    fillSpreadContent(leftPage, rightPage, pageData.data);
    
    // Закриваємо шаблон
    templateDoc.close(SaveOptions.NO);
}

// Заповнює контент обкладинки
function fillCoverContent(page, data) {
    // Шукаємо фрейми по Script Labels
    var items = page.allPageItems;
    
    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        var label = item.label;
        
        try {
            if (label === 'COVER_IMAGE' && data.image1) {
                // Вставляємо фото
                placeImage(item, data.image1);
            } else if (label === 'COVER_TITLE' && data.title) {
                // Вставляємо заголовок
                setText(item, data.title);
            } else if (label === 'COVER_SUB' && data.subtitle) {
                // Вставляємо підзаголовок
                setText(item, data.subtitle);
            }
        } catch (e) {
            $.writeln('Помилка при заповненні ' + label + ': ' + e.message);
        }
    }
}

// Заповнює контент розвороту
function fillSpreadContent(leftPage, rightPage, data) {
    // Ліва сторінка
    var leftItems = leftPage.allPageItems;
    for (var i = 0; i < leftItems.length; i++) {
        var item = leftItems[i];
        var label = item.label;
        
        try {
            if (label === 'L_IMG1' && data.left.image1) {
                placeImage(item, data.left.image1);
            } else if (label === 'L_TITLE' && data.left.title) {
                setText(item, data.left.title);
            } else if (label === 'L_QUOTE' && data.left.quote) {
                setText(item, data.left.quote);
            }
        } catch (e) {
            $.writeln('Помилка на лівій сторінці ' + label + ': ' + e.message);
        }
    }
    
    // Права сторінка
    var rightItems = rightPage.allPageItems;
    for (var i = 0; i < rightItems.length; i++) {
        var item = rightItems[i];
        var label = item.label;
        
        try {
            if (label === 'R_IMG1' && data.right.image1) {
                placeImage(item, data.right.image1);
            } else if (label === 'R_NAME' && data.right.name) {
                setText(item, data.right.name);
            } else if (label === 'R_BIO' && data.right.bio) {
                setText(item, data.right.bio);
            } else if (label === 'R_FACTS' && data.right.facts) {
                setText(item, data.right.facts.join('\n'));
            }
        } catch (e) {
            $.writeln('Помилка на правій сторінці ' + label + ': ' + e.message);
        }
    }
}

// Вставляє зображення у фрейм
function placeImage(frame, imagePath) {
    // Шлях відносно проекту
    var projectDir = new Folder($.fileName).parent.parent;
    var fullPath = projectDir + '/' + imagePath;
    var imageFile = new File(fullPath);
    
    if (!imageFile.exists) {
        $.writeln('Зображення не знайдено: ' + fullPath);
        return;
    }
    
    // Видаляємо старий контент якщо є
    if (frame.allGraphics.length > 0) {
        frame.allGraphics[0].remove();
    }
    
    // Вставляємо нове зображення
    frame.place(imageFile);
    
    // Підганяємо розмір (fit proportionally + center)
    if (frame.allGraphics.length > 0) {
        frame.fit(FitOptions.FILL_PROPORTIONALLY);
        frame.fit(FitOptions.CENTER_CONTENT);
    }
}

// Встановлює текст у фрейм
function setText(frame, text) {
    if (frame.constructor.name === 'TextFrame') {
        frame.contents = text;
    }
}

// Експортує результати
function exportResults(doc, outputDir, projectName) {
    var baseName = projectName || 'magazine';
    
    // Зберігаємо INDD
    var inddFile = new File(outputDir + '/' + baseName + '.indd');
    doc.save(inddFile);
    
    // Експортуємо PDF
    var pdfFile = new File(outputDir + '/' + baseName + '.pdf');
    
    var pdfPreset = app.pdfExportPresets.item('[High Quality Print]');
    
    doc.exportFile(
        ExportFormat.PDF_TYPE,
        pdfFile,
        false,
        pdfPreset
    );
    
    $.writeln('Збережено:');
    $.writeln('  INDD: ' + inddFile.fsName);
    $.writeln('  PDF: ' + pdfFile.fsName);
}

// Запуск
main();
