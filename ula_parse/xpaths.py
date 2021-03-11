xpath_selectors = {
        'pagination': "//a[contains(@class, 'HH-Pager-Control')]/@href",
        'vacancies': "//a[contains(@data-qa, 'vacancy-serp__vacancy-title')]/@href",
        'employer': "//a[@data-qa='vacancy-company-name']/@href",
        'employer_vacancies': "//a[@data-qa='employer-page__employer-vacancies-link']/@href"
    }

vacancies_xpath = {
            'title': "//h1[@data-qa='vacancy-title']/text()",
            'salary': "//p[@class='vacancy-salary']//text()",
            'description': "//div[@data-qa='vacancy-description']//text()",
            'skills': "//span[@data-qa='bloko-tag__text']//text()",
            'employer_url': "//a[@data-qa='vacancy-company-name']/@href"
        }

employer_xpath = {
            'company_name': "//span[@data-qa='company-header-title-name']/text()",
            'operational_fields': "//div[text()='Сферы деятельности']/following-sibling::p/text()",
            'description': "//div[@data-qa='company-description-text']//text()"
        }