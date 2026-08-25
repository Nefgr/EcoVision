import streamlit as st
from ai_client import analyze_image
from waste_rules import get_rule

st.set_page_config(page_title="EcoVision", page_icon="♻️")

st.title("♻️ EcoVision")
st.write("Загрузи или сфотографируй отход, чтобы узнать, как его правильно утилизировать")

# --- Загрузка изображения ---
tab1, tab2 = st.tabs(["Загрузить фото", "Сделать фото"])

uploaded_image = None

with tab1:
    uploaded_file = st.file_uploader(
        "Выбери фотографию",
        type=["jpg", "jpeg", "png"],
    )
    if uploaded_file is not None:
        uploaded_image = uploaded_file

with tab2:
    camera_photo = st.camera_input("Сфотографируй объект")
    if camera_photo is not None:
        uploaded_image = camera_photo

# --- Показ превью и кнопка анализа ---
if uploaded_image is not None:
    st.image(uploaded_image, caption="Твоё фото", use_container_width=True)

    # Ограничение размера файла — не больше 10 МБ (простая проверка безопасности)
    if uploaded_image.size > 10 * 1024 * 1024:
        st.error("Файл слишком большой (максимум 10 МБ). Загрузи фото меньшего размера.")
    else:
        if st.button("Анализировать", type="primary"):
            with st.spinner("AI анализирует фото..."):
                image_bytes = uploaded_image.getvalue()
                mime_type = uploaded_image.type  # например "image/jpeg"
                result = analyze_image(image_bytes, mime_type)

            # --- Обработка результата ---
            status = result.get("status")

            if status == "error":
                st.error("Сервис AI временно недоступен. Попробуй ещё раз чуть позже.")

            elif status == "unclear_image":
                st.warning(
                    "Не удалось разобрать, что на фото. Попробуй сфотографировать при "
                    "лучшем освещении и так, чтобы объект был виден крупно и чётко."
                )

            elif status == "multiple_objects":
                st.warning(
                    "На фото похоже несколько разных объектов. "
                    "Попробуй сфотографировать по одному предмету за раз."
                )

            else:
                # status == "ok" или "low_confidence"
                rule = get_rule(result.get("category_code"))

                st.divider()
                st.subheader(f"Объект: {result.get('object_name', 'неизвестно')}")
                st.write(f"**Категория:** {rule['title']}")
                st.write(f"**Рекомендация по утилизации:** {rule['advice']}")

                if status == "low_confidence":
                    st.info(
                        "⚠️ AI не полностью уверен в результате. "
                        "Если результат выглядит неверным — попробуй переснять фото."
                    )

    if st.button("Проверить ещё раз"):
        st.rerun()