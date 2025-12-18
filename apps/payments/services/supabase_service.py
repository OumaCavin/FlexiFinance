"""
Supabase Service for FlexiFinance
Handles database operations and contact form submissions
"""
import logging
import requests
import json
from django.conf import settings

logger = logging.getLogger(__name__)


class SupabaseService:
    """
    Supabase Integration Service
    Provides database operations for contact forms and additional data
    """
    
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_ANON_KEY
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def submit_contact_form(self, contact_data):
        """
        Submit contact form to Supabase
        
        Args:
            contact_data (dict): Contact form data with keys:
                - name (str): Contact name
                - email (str): Contact email
                - phone (str): Contact phone
                - subject (str): Message subject
                - message (str): Message content
                - source (str): Source of submission
            
        Returns:
            dict: Submission result
        """
        try:
            data = {
                'name': contact_data.get('name', ''),
                'email': contact_data.get('email', ''),
                'phone': contact_data.get('phone', ''),
                'subject': contact_data.get('subject', 'General Inquiry'),
                'message': contact_data.get('message', ''),
                'source': contact_data.get('source', 'website'),
                'status': 'new',
                'created_at': contact_data.get('created_at', 'now()'),
                'ip_address': contact_data.get('ip_address', ''),
                'user_agent': contact_data.get('user_agent', '')
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/contact_submissions",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"Contact form submitted: {result[0]['id'] if result else 'unknown'}")
                return {
                    'success': True,
                    'submission_id': result[0]['id'] if result else None,
                    'message': 'Contact form submitted successfully'
                }
            else:
                logger.error(f"Contact form submission failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Failed to submit form: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Contact form submission error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_contact_submissions(self, limit=50, status=None):
        """
        Retrieve contact form submissions
        
        Args:
            limit (int): Maximum number of submissions
            status (str): Filter by status
            
        Returns:
            dict: Contact submissions
        """
        try:
            url = f"{self.supabase_url}/rest/v1/contact_submissions"
            params = {'limit': limit}
            
            if status:
                params['status'] = f'eq.{status}'
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                submissions = response.json()
                return {
                    'success': True,
                    'submissions': submissions,
                    'count': len(submissions)
                }
            else:
                logger.error(f"Failed to get submissions: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Failed to retrieve submissions: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Get submissions error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_submission_status(self, submission_id, status):
        """
        Update contact submission status
        
        Args:
            submission_id (str): Submission ID
            status (str): New status
            
        Returns:
            dict: Update result
        """
        try:
            data = {'status': status}
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/contact_submissions?id=eq.{submission_id}",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 204:
                logger.info(f"Submission status updated: {submission_id} -> {status}")
                return {
                    'success': True,
                    'message': 'Status updated successfully'
                }
            else:
                logger.error(f"Status update failed: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Failed to update status: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Status update error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def store_user_feedback(self, user_id, feedback_type, content, rating=None):
        """
        Store user feedback in Supabase
        
        Args:
            user_id (str): User ID
            feedback_type (str): Type of feedback
            content (str): Feedback content
            rating (int): Rating (1-5)
            
        Returns:
            dict: Storage result
        """
        try:
            data = {
                'user_id': user_id,
                'feedback_type': feedback_type,
                'content': content,
                'rating': rating,
                'created_at': 'now()'
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/user_feedback",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"User feedback stored: {result[0]['id'] if result else 'unknown'}")
                return {
                    'success': True,
                    'feedback_id': result[0]['id'] if result else None
                }
            else:
                logger.error(f"Feedback storage failed: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Failed to store feedback: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Feedback storage error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_newsletter_subscription(self, email, source='website'):
        """
        Create newsletter subscription
        
        Args:
            email (str): Email address
            source (str): Source of subscription
            
        Returns:
            dict: Subscription result
        """
        try:
            data = {
                'email': email,
                'source': source,
                'subscribed_at': 'now()',
                'active': True
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/newsletter_subscriptions",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 201:
                logger.info(f"Newsletter subscription created: {email}")
                return {
                    'success': True,
                    'message': 'Successfully subscribed to newsletter'
                }
            else:
                logger.error(f"Newsletter subscription failed: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Failed to create subscription: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Newsletter subscription error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_newsletter_subscriptions(self, limit=100):
        """
        Get newsletter subscriptions
        
        Args:
            limit (int): Maximum number of subscriptions
            
        Returns:
            dict: Subscriptions data
        """
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/newsletter_subscriptions",
                headers=self.headers,
                params={'limit': limit, 'active': 'eq.true'}
            )
            
            if response.status_code == 200:
                subscriptions = response.json()
                return {
                    'success': True,
                    'subscriptions': subscriptions,
                    'count': len(subscriptions)
                }
            else:
                logger.error(f"Failed to get subscriptions: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Failed to retrieve subscriptions: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Get subscriptions error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def health_check(self):
        """
        Check Supabase service health
        
        Returns:
            bool: True if service is healthy
        """
        try:
            # Try to make a simple request to check connectivity
            response = requests.get(
                f"{self.supabase_url}/rest/v1/contact_submissions",
                headers=self.headers,
                params={'limit': 1}
            )
            return response.status_code in [200, 404]  # 404 is okay if table doesn't exist
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False