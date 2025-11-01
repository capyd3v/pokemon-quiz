
class PokemonQuiz {
    constructor() {
        this.correctCount = 0;
        this.wrongCount = 0;
        this.currentPokemon = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Botones de opción
        document.querySelectorAll('.option-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.checkAnswer(e.target));
        });

        // Botón siguiente
        document.getElementById('next-btn').addEventListener('click', () => {
            this.nextPokemon();
        });
    }

    async checkAnswer(selectedButton) {
        const selectedName = selectedButton.getAttribute('data-name');
        const correctAnswer = document.getElementById('correct-answer').value;
        
        // Deshabilitar todos los botones
        document.querySelectorAll('.option-btn').forEach(btn => {
            btn.disabled = true;
        });

        // Mostrar la imagen del Pokémon
        document.getElementById('pokemon-sprite').classList.add('revealed');

        // Marcar respuestas correctas/incorrectas
        document.querySelectorAll('.option-btn').forEach(btn => {
            const name = btn.getAttribute('data-name');
            if (name === correctAnswer) {
                btn.classList.add('correct');
            } else if (name === selectedName && name !== correctAnswer) {
                btn.classList.add('wrong');
            }
        });

        const feedback = document.getElementById('feedback');
        
        if (selectedName === correctAnswer) {
            feedback.textContent = `¡Correcto! Es ${correctAnswer}`;
            feedback.className = 'feedback correct';
            this.correctCount++;
        } else {
            feedback.textContent = `Incorrecto. Era ${correctAnswer}`;
            feedback.className = 'feedback wrong';
            this.wrongCount++;
        }

        // Actualizar estadísticas
        document.getElementById('correct-count').textContent = this.correctCount;
        document.getElementById('wrong-count').textContent = this.wrongCount;

        // Mostrar botón siguiente
        document.getElementById('next-btn').style.display = 'block';
    }

    async nextPokemon() {
        try {
            const response = await fetch('/next-pokemon');
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.updateUI(data);
        } catch (error) {
            console.error('Error al obtener siguiente Pokémon:', error);
            alert('Error al cargar el siguiente Pokémon. Recargando la página...');
            location.reload();
        }
    }

    updateUI(pokemonData) {
        // Actualizar imagen
        const sprite = document.getElementById('pokemon-sprite');
        sprite.src = pokemonData.sprite;
        sprite.classList.remove('revealed');

        // Actualizar tipos
        const typesContainer = document.getElementById('types-container');
        typesContainer.innerHTML = pokemonData.types.map(type => 
            `<span class="type-badge type-${type}">${type.charAt(0).toUpperCase() + type.slice(1)}</span>`
        ).join('');

        // Actualizar opciones
        const optionsContainer = document.querySelector('.options-grid');
        optionsContainer.innerHTML = pokemonData.options.map(option => 
            `<button type="button" class="option-btn" data-name="${option}">
                ${option.charAt(0).toUpperCase() + option.slice(1)}
            </button>`
        ).join('');

        // Actualizar respuesta correcta
        document.getElementById('correct-answer').value = pokemonData.correct_answer;

        // Reiniciar estado UI
        document.getElementById('feedback').textContent = '';
        document.getElementById('feedback').className = 'feedback';
        document.getElementById('next-btn').style.display = 'none';

        // Re-inicializar event listeners para los nuevos botones
        document.querySelectorAll('.option-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.checkAnswer(e.target));
        });
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new PokemonQuiz();
});
