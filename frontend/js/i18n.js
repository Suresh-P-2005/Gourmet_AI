const translations = {
    "English": {
        "generate_btn": "✨ Generate Recipe",
        "ingredients_placeholder": "e.g. Chicken breast, broccoli, garlic...",
        "cuisine_label": "Cuisine Style (Optional)",
        "cuisine_placeholder": "e.g. Italian, Mexican, Thai...",
        "dietary_label": "Dietary Preferences (Optional)",
        "dietary_placeholder": "e.g. Vegetarian, Keto, Low Carb..."
    },
    "Hindi": {
        "generate_btn": "✨ रेसिपी बनाएं",
        "ingredients_placeholder": "जैसे कि चिकन, चावल, लहसुन...",
        "cuisine_label": "व्यंजन शैली (वैकल्पिक)",
        "cuisine_placeholder": "जैसे इतालवी, मैक्सिकन, थाई...",
        "dietary_label": "आहार प्राथमिकताएं (वैकल्पिक)",
        "dietary_placeholder": "जैसे शाकाहारी, कीटो, लो कार्ब..."
    },
    "Bengali": {
        "generate_btn": "✨ রেসিপি তৈরি করুন",
        "ingredients_placeholder": "যেমন মুরগি, ব্রকলি, রসুন...",
        "cuisine_label": "রন্ধনশৈলী (ঐচ্ছিক)",
        "cuisine_placeholder": "যেমন ইতালীয়, মেক্সিকান, থাই...",
        "dietary_label": "খাদ্যতালিকাগত পছন্দ (ঐচ্ছিক)",
        "dietary_placeholder": "যেমন নিরামিষ, কিটো..."
    },
    "Telugu": {
        "generate_btn": "✨ రెసిపీని సృష్టించండి",
        "ingredients_placeholder": "ఉదా. చికెన్, బ్రోకలీ, వెల్లుల్లి...",
        "cuisine_label": "వంట శైలి (ఐచ్ఛికం)",
        "cuisine_placeholder": "ఉదా. ఇటాలియన్, మెక్సికన్, థాయ్...",
        "dietary_label": "ఆహార ప్రాధాన్యతలు (ఐచ్ఛికం)",
        "dietary_placeholder": "ఉదా. శాఖాహారం, కీటో..."
    },
    "Tamil": {
        "generate_btn": "✨ செய்முறையை உருவாக்கு",
        "ingredients_placeholder": "எ.கா. கோழி, பூண்டு...",
        "cuisine_label": "உணவு முறை (விருப்பப்படி)",
        "cuisine_placeholder": "எ.கா. இத்தாலியன், மெக்சிகன்...",
        "dietary_label": "உணவு விருப்பங்கள் (விருப்பப்படி)",
        "dietary_placeholder": "எ.கா. சைவம், கீட்டோ..."
    },
    "Marathi": {
        "generate_btn": "✨ रेसिपी तयार करा",
        "ingredients_placeholder": "उदा. चिकन, ब्रोकोली, लसूण...",
        "cuisine_label": "पाककृती शैली (पर्यायी)",
        "cuisine_placeholder": "उदा. इटालियन, मेक्सिकन, थाई...",
        "dietary_label": "आहारातील प्राधान्ये (पर्यायी)",
        "dietary_placeholder": "उदा. शाकाहारी, कीटो..."
    },
    "Gujarati": {
        "generate_btn": "✨ રેસીપી બનાવો",
        "ingredients_placeholder": "દા.ત. ચિકન, બ્રોકોલી, લસણ...",
        "cuisine_label": "રસોઈ શૈલી (વૈકલ્પિક)",
        "cuisine_placeholder": "દા.ત. ઇટાલિયન, મેક્સીકન...",
        "dietary_label": "આહાર પસંદગીઓ (વૈકલ્પિક)",
        "dietary_placeholder": "દા.ત. શાકાહારી, કીટો..."
    },
    "Kannada": {
        "generate_btn": "✨ ಪಾಕವಿಧಾನ ರಚಿಸಿ",
        "ingredients_placeholder": "ಉದಾ. ಚಿಕನ್, ಬ್ರೊಕೊಲಿ, ಬೆಳ್ಳುಳ್ಳಿ...",
        "cuisine_label": "ಶೈಲಿ (ಐಚ್ಛಿಕ)",
        "cuisine_placeholder": "ಉದಾ. ಇಟಾಲಿಯನ್, ಮೆಕ್ಸಿಕನ್...",
        "dietary_label": "ಆಹಾರದ ಆದ್ಯತೆಗಳು (ಐಚ್ಛಿಕ)",
        "dietary_placeholder": "ಉದಾ. ಸಸ್ಯಾಹಾರಿ, ಕೀಟೋ..."
    },
    "Malayalam": {
        "generate_btn": "✨ പാചകക്കുറിപ്പ് ഉണ്ടാക്കുക",
        "ingredients_placeholder": "ഉദാ. ചിക്കൻ, വെളുത്തുള്ളി...",
        "cuisine_label": "ശൈലി (ഓപ്ഷണൽ)",
        "cuisine_placeholder": "ഉദാ. ഇറ്റാലിയൻ, മെക്സിക്കൻ...",
        "dietary_label": "ഭക്ഷണ മുൻഗണനകൾ (ഓപ്ഷണൽ)",
        "dietary_placeholder": "ഉദാ. വെജിറ്റേറിയൻ, കീറ്റോ..."
    },
    "Urdu": {
        "generate_btn": "✨ ترکیب بنائیں",
        "ingredients_placeholder": "مثلاً چکن، لہسن...",
        "cuisine_label": "طرزِ طعام (اختیاری)",
        "cuisine_placeholder": "مثلاً اطالوی، میکسیکن...",
        "dietary_label": "غذائی ترجیحات (اختیاری)",
        "dietary_placeholder": "مثلاً سبزی خور، کیٹو..."
    },
    "Punjabi": {
        "generate_btn": "✨ ਵਿਅੰਜਨ ਬਣਾਓ",
        "ingredients_placeholder": "ਉਦਾਹਰਣ ਲਈ ਚਿਕਨ, ਲਸਣ...",
        "cuisine_label": "ਪਕਵਾਨ ਸ਼ੈਲੀ (ਵਿਕਲਪਿਕ)",
        "cuisine_placeholder": "ਉਦਾਹਰਣ ਲਈ ਇਤਾਲਵੀ, ਮੈਕਸੀਕਨ...",
        "dietary_label": "ਖੁਰਾਕ ਤਰਜੀਹਾਂ (ਵਿਕਲਪਿਕ)",
        "dietary_placeholder": "ਉਦਾਹਰਣ ਲਈ ਸ਼ਾਕਾਹਾਰੀ, ਕੀਟੋ..."
    },
    "Odia": {
        "generate_btn": "✨ ରେସିପି ପ୍ରସ୍ତୁତ କରନ୍ତୁ",
        "ingredients_placeholder": "ଉଦାହରଣ ସ୍ୱରୂପ ଚିକେନ୍, ରସୁଣ...",
        "cuisine_label": "ରନ୍ଧନ ଶୈଳୀ (ଇଚ୍ଛାଧୀନ)",
        "cuisine_placeholder": "ଉଦାହରଣ ସ୍ୱରୂପ ଇଟାଲୀୟ...",
        "dietary_label": "ଖାଦ୍ୟ ପସନ୍ଦ (ଇଚ୍ଛାଧୀନ)",
        "dietary_placeholder": "ଉଦାହରଣ ସ୍ୱରୂପ ଶାକାହାରୀ..."
    },
    "Assamese": {
        "generate_btn": "✨ ৰেচিপি প্ৰস্তুত কৰক",
        "ingredients_placeholder": "যেনে- কুকুৰা, নহৰু...",
        "cuisine_label": "ৰন্ধনশৈলী (বিকল্প)",
        "cuisine_placeholder": "যেনে- ইটালীয়, মেক্সিকান...",
        "dietary_label": "খাদ্যৰ পছন্দ (বিকল্প)",
        "dietary_placeholder": "যেনে- নিৰামিষ, কিটো..."
    }
};

function applyTranslations() {
    const lang = localStorage.getItem("app_lang") || "English";
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (translations[lang] && translations[lang][key]) {
            if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
                el.placeholder = translations[lang][key];
            } else {
                // Preserve .label-hint if it exists
                const hint = el.querySelector('.label-hint');
                if (hint) {
                    el.innerHTML = translations[lang][key] + " ";
                    el.appendChild(hint);
                } else {
                    el.innerHTML = translations[lang][key];
                }
            }
        }
    });
}

function initI18n() {
    const switcher = document.getElementById("languageSwitcher");
    if (switcher) {
        switcher.value = localStorage.getItem("app_lang") || "English";
        switcher.addEventListener("change", (e) => {
            localStorage.setItem("app_lang", e.target.value);
            applyTranslations();
        });
    }
    applyTranslations();
}

document.addEventListener("DOMContentLoaded", initI18n);
