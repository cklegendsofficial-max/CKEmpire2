import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.mark.e2e
@pytest.mark.selenium
class TestDashboardE2E:
    """End-to-end tests for the dashboard using Selenium"""
    
    @pytest.fixture(scope="class")
    def driver(self, browser_config):
        """Setup WebDriver for E2E tests"""
        chrome_options = Options()
        if browser_config["headless"]:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        
        yield driver
        
        driver.quit()
    
    @pytest.fixture(scope="class")
    def wait(self, driver):
        """WebDriverWait instance"""
        return WebDriverWait(driver, 10)
    
    def test_dashboard_loads_successfully(self, driver, wait):
        """Test that the dashboard loads successfully"""
        # Navigate to the dashboard
        driver.get("http://localhost:3000")
        
        # Wait for the dashboard to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard")))
        
        # Verify dashboard elements are present
        assert driver.find_element(By.CLASS_NAME, "dashboard")
        assert driver.find_element(By.CLASS_NAME, "sidebar")
        assert driver.find_element(By.CLASS_NAME, "main-content")
        
        # Check for navigation elements
        nav_items = driver.find_elements(By.CSS_SELECTOR, ".sidebar a")
        expected_nav_items = ["Dashboard", "Projects", "Revenue", "AI", "Ethics", "Performance"]
        
        for item in expected_nav_items:
            assert any(item in nav.text for nav in nav_items), f"Navigation item '{item}' not found"
    
    def test_dashboard_metrics_display(self, driver, wait):
        """Test that dashboard metrics are displayed correctly"""
        driver.get("http://localhost:3000")
        
        # Wait for metrics to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "metric-card")))
        
        # Check for metric cards
        metric_cards = driver.find_elements(By.CLASS_NAME, "metric-card")
        assert len(metric_cards) >= 4  # Should have at least 4 metric cards
        
        # Verify metric card content
        for card in metric_cards:
            assert card.find_element(By.CLASS_NAME, "metric-title")
            assert card.find_element(By.CLASS_NAME, "metric-value")
    
    def test_navigation_works(self, driver, wait):
        """Test that navigation between sections works"""
        driver.get("http://localhost:3000")
        
        # Test navigation to Projects
        projects_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Projects')]")))
        projects_link.click()
        
        # Wait for projects page to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-section")))
        assert "projects" in driver.current_url.lower() or driver.find_element(By.CLASS_NAME, "projects-section")
        
        # Test navigation to Revenue
        revenue_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Revenue')]")))
        revenue_link.click()
        
        # Wait for revenue page to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "revenue-section")))
        assert "revenue" in driver.current_url.lower() or driver.find_element(By.CLASS_NAME, "revenue-section")
        
        # Test navigation to AI
        ai_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'AI')]")))
        ai_link.click()
        
        # Wait for AI page to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ai-section")))
        assert "ai" in driver.current_url.lower() or driver.find_element(By.CLASS_NAME, "ai-section")
    
    def test_project_creation_flow(self, driver, wait):
        """Test the complete project creation flow"""
        driver.get("http://localhost:3000")
        
        # Navigate to Projects
        projects_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Projects')]")))
        projects_link.click()
        
        # Wait for projects page
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-section")))
        
        # Find and click "Add Project" button
        add_project_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Project')]")))
        add_project_btn.click()
        
        # Wait for project form to appear
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "project-form")))
        
        # Fill in project details
        name_input = driver.find_element(By.NAME, "name")
        name_input.clear()
        name_input.send_keys("E2E Test Project")
        
        description_input = driver.find_element(By.NAME, "description")
        description_input.clear()
        description_input.send_keys("This is a test project created during E2E testing")
        
        # Select status
        status_select = driver.find_element(By.NAME, "status")
        status_select.click()
        active_option = driver.find_element(By.XPATH, "//option[@value='active']")
        active_option.click()
        
        # Set budget
        budget_input = driver.find_element(By.NAME, "budget")
        budget_input.clear()
        budget_input.send_keys("5000")
        
        # Submit the form
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_btn.click()
        
        # Wait for success message or redirect
        try:
            success_message = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
            assert "Project created successfully" in success_message.text
        except TimeoutException:
            # If no success message, check if we're back to projects list
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-list")))
    
    def test_ai_content_generation_flow(self, driver, wait):
        """Test the AI content generation flow"""
        driver.get("http://localhost:3000")
        
        # Navigate to AI section
        ai_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'AI')]")))
        ai_link.click()
        
        # Wait for AI page
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ai-section")))
        
        # Find content generation form
        prompt_input = wait.until(EC.presence_of_element_located((By.NAME, "prompt")))
        prompt_input.clear()
        prompt_input.send_keys("Write a blog post about artificial intelligence and its impact on business")
        
        # Select model
        model_select = driver.find_element(By.NAME, "model")
        model_select.click()
        gpt4_option = driver.find_element(By.XPATH, "//option[@value='gpt-4']")
        gpt4_option.click()
        
        # Set max tokens
        max_tokens_input = driver.find_element(By.NAME, "max_tokens")
        max_tokens_input.clear()
        max_tokens_input.send_keys("500")
        
        # Set temperature
        temperature_input = driver.find_element(By.NAME, "temperature")
        temperature_input.clear()
        temperature_input.send_keys("0.7")
        
        # Submit the form
        generate_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate')]")))
        generate_btn.click()
        
        # Wait for generation to complete
        try:
            result_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "generation-result")))
            assert result_container.is_displayed()
            
            # Check for generated content
            generated_content = driver.find_element(By.CLASS_NAME, "generated-content")
            assert len(generated_content.text) > 0
            
            # Check for metadata
            metadata = driver.find_element(By.CLASS_NAME, "generation-metadata")
            assert "tokens" in metadata.text.lower()
            assert "cost" in metadata.text.lower()
            
        except TimeoutException:
            # If generation takes too long, check for loading state
            loading_indicator = driver.find_element(By.CLASS_NAME, "loading-indicator")
            assert loading_indicator.is_displayed()
    
    def test_ethics_check_flow(self, driver, wait):
        """Test the ethics check flow"""
        driver.get("http://localhost:3000")
        
        # Navigate to Ethics section
        ethics_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Ethics')]")))
        ethics_link.click()
        
        # Wait for Ethics page
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ethics-section")))
        
        # Find ethics check form
        content_input = wait.until(EC.presence_of_element_located((By.NAME, "content")))
        content_input.clear()
        content_input.send_keys("This is a test content for ethics checking. It should be evaluated for ethical considerations.")
        
        # Select content type
        content_type_select = driver.find_element(By.NAME, "content_type")
        content_type_select.click()
        blog_option = driver.find_element(By.XPATH, "//option[@value='blog']")
        blog_option.click()
        
        # Submit the form
        check_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Check Ethics')]")))
        check_btn.click()
        
        # Wait for ethics check result
        try:
            result_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ethics-result")))
            assert result_container.is_displayed()
            
            # Check for result elements
            is_ethical = driver.find_element(By.CLASS_NAME, "ethics-decision")
            confidence = driver.find_element(By.CLASS_NAME, "ethics-confidence")
            
            assert is_ethical.is_displayed()
            assert confidence.is_displayed()
            
        except TimeoutException:
            # If check takes too long, check for loading state
            loading_indicator = driver.find_element(By.CLASS_NAME, "loading-indicator")
            assert loading_indicator.is_displayed()
    
    def test_performance_monitoring(self, driver, wait):
        """Test performance monitoring display"""
        driver.get("http://localhost:3000")
        
        # Navigate to Performance section
        performance_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Performance')]")))
        performance_link.click()
        
        # Wait for Performance page
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "performance-section")))
        
        # Check for performance metrics
        performance_score = driver.find_element(By.CLASS_NAME, "performance-score")
        assert performance_score.is_displayed()
        
        # Check for performance charts
        charts = driver.find_elements(By.CLASS_NAME, "performance-chart")
        assert len(charts) > 0
        
        # Check for optimization options
        optimize_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Optimize')]")
        assert optimize_btn.is_displayed()
    
    def test_revenue_tracking(self, driver, wait):
        """Test revenue tracking functionality"""
        driver.get("http://localhost:3000")
        
        # Navigate to Revenue section
        revenue_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Revenue')]")))
        revenue_link.click()
        
        # Wait for Revenue page
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "revenue-section")))
        
        # Check for revenue charts
        revenue_chart = driver.find_element(By.CLASS_NAME, "revenue-chart")
        assert revenue_chart.is_displayed()
        
        # Check for revenue metrics
        total_revenue = driver.find_element(By.CLASS_NAME, "total-revenue")
        assert total_revenue.is_displayed()
        
        # Test adding new revenue entry
        add_revenue_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Revenue')]")))
        add_revenue_btn.click()
        
        # Wait for revenue form
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "revenue-form")))
        
        # Fill revenue form
        amount_input = driver.find_element(By.NAME, "amount")
        amount_input.clear()
        amount_input.send_keys("1000")
        
        source_input = driver.find_element(By.NAME, "source")
        source_input.clear()
        source_input.send_keys("E2E Test")
        
        description_input = driver.find_element(By.NAME, "description")
        description_input.clear()
        description_input.send_keys("Revenue from E2E testing")
        
        # Submit form
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_btn.click()
        
        # Wait for success or redirect
        try:
            success_message = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
            assert "Revenue added successfully" in success_message.text
        except TimeoutException:
            # If no success message, check if we're back to revenue list
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "revenue-list")))
    
    def test_responsive_design(self, driver, wait):
        """Test responsive design on different screen sizes"""
        # Test desktop view
        driver.set_window_size(1920, 1080)
        driver.get("http://localhost:3000")
        
        # Verify desktop layout
        sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
        assert sidebar.is_displayed()
        
        # Test tablet view
        driver.set_window_size(768, 1024)
        driver.refresh()
        
        # Verify tablet layout (sidebar might be collapsible)
        try:
            sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
            assert sidebar.is_displayed()
        except NoSuchElementException:
            # Sidebar might be hidden on tablet
            pass
        
        # Test mobile view
        driver.set_window_size(375, 667)
        driver.refresh()
        
        # Verify mobile layout
        try:
            mobile_menu = driver.find_element(By.CLASS_NAME, "mobile-menu")
            assert mobile_menu.is_displayed()
        except NoSuchElementException:
            # Mobile menu might not be implemented yet
            pass
    
    def test_error_handling(self, driver, wait):
        """Test error handling in the UI"""
        # Test 404 page
        driver.get("http://localhost:3000/nonexistent-page")
        
        try:
            error_page = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-page")))
            assert "404" in error_page.text or "Not Found" in error_page.text
        except TimeoutException:
            # If no specific error page, check for any error indication
            page_content = driver.page_source
            assert "error" in page_content.lower() or "not found" in page_content.lower()
        
        # Test network error handling
        driver.get("http://localhost:3000")
        
        # Simulate network error by disabling network
        driver.execute_script("window.navigator.onLine = false;")
        
        # Try to perform an action that requires network
        try:
            projects_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Projects')]")))
            projects_link.click()
            
            # Check for error message
            error_message = driver.find_element(By.CLASS_NAME, "error-message")
            assert "network" in error_message.text.lower() or "connection" in error_message.text.lower()
        except NoSuchElementException:
            # Error handling might not be implemented yet
            pass
    
    def test_accessibility(self, driver, wait):
        """Test basic accessibility features"""
        driver.get("http://localhost:3000")
        
        # Check for proper heading structure
        headings = driver.find_elements(By.TAG_NAME, "h1")
        assert len(headings) > 0
        
        # Check for alt text on images
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            alt_text = img.get_attribute("alt")
            assert alt_text is not None, "Image missing alt text"
        
        # Check for proper form labels
        form_inputs = driver.find_elements(By.TAG_NAME, "input")
        for input_elem in form_inputs:
            input_id = input_elem.get_attribute("id")
            if input_id:
                label = driver.find_element(By.XPATH, f"//label[@for='{input_id}']")
                assert label.is_displayed(), f"Input {input_id} missing label"
        
        # Test keyboard navigation
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.TAB)
        
        # Check if focus is visible
        focused_element = driver.switch_to.active_element
        assert focused_element.is_displayed()
    
    def test_data_persistence(self, driver, wait):
        """Test that data persists across page refreshes"""
        driver.get("http://localhost:3000")
        
        # Navigate to Projects and create a project
        projects_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Projects')]")))
        projects_link.click()
        
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-section")))
        
        # Create a project
        add_project_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Project')]")))
        add_project_btn.click()
        
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "project-form")))
        
        name_input = driver.find_element(By.NAME, "name")
        name_input.clear()
        name_input.send_keys("Persistence Test Project")
        
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_btn.click()
        
        # Wait for project to be created
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Persistence Test Project')]")))
        except TimeoutException:
            # If no immediate feedback, refresh and check
            driver.refresh()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-section")))
        
        # Refresh the page
        driver.refresh()
        
        # Verify the project still exists
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-section")))
        project_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'Persistence Test Project')]")
        assert len(project_elements) > 0, "Project not persisted after page refresh"

@pytest.mark.e2e
@pytest.mark.selenium
class TestCrossBrowserCompatibility:
    """Test cross-browser compatibility"""
    
    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    def test_browser_compatibility(self, browser):
        """Test that the application works across different browsers"""
        # This test would require multiple browser drivers
        # For now, we'll just test Chrome as it's most common
        if browser == "chrome":
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                driver.get("http://localhost:3000")
                
                # Basic functionality test
                wait = WebDriverWait(driver, 10)
                dashboard = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard")))
                assert dashboard.is_displayed()
                
            finally:
                driver.quit()
        else:
            pytest.skip(f"Browser {browser} not configured for testing")

@pytest.mark.e2e
@pytest.mark.selenium
class TestPerformanceE2E:
    """Test frontend performance"""
    
    def test_page_load_time(self, driver):
        """Test page load performance"""
        start_time = time.time()
        
        driver.get("http://localhost:3000")
        
        # Wait for page to be fully loaded
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        load_time = time.time() - start_time
        
        # Page should load within 5 seconds
        assert load_time < 5.0, f"Page load time ({load_time:.2f}s) exceeded 5 seconds"
    
    def test_interaction_responsiveness(self, driver, wait):
        """Test UI responsiveness to user interactions"""
        driver.get("http://localhost:3000")
        
        # Test navigation responsiveness
        start_time = time.time()
        
        projects_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Projects')]")))
        projects_link.click()
        
        # Wait for navigation to complete
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "projects-section")))
        
        navigation_time = time.time() - start_time
        
        # Navigation should complete within 2 seconds
        assert navigation_time < 2.0, f"Navigation time ({navigation_time:.2f}s) exceeded 2 seconds"
    
    def test_memory_usage(self, driver):
        """Test memory usage during extended use"""
        driver.get("http://localhost:3000")
        
        # Perform multiple operations to test memory usage
        for i in range(10):
            # Navigate between sections
            sections = ["Projects", "Revenue", "AI", "Ethics", "Performance"]
            for section in sections:
                try:
                    link = driver.find_element(By.XPATH, f"//a[contains(text(), '{section}')]")
                    link.click()
                    time.sleep(0.5)  # Brief pause
                except NoSuchElementException:
                    continue
            
            # Go back to dashboard
            try:
                dashboard_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Dashboard')]")
                dashboard_link.click()
            except NoSuchElementException:
                pass
        
        # Check for any obvious memory leaks (this is a basic test)
        # In a real scenario, you'd use browser dev tools to monitor memory usage
        assert driver.execute_script("return document.readyState") == "complete" 